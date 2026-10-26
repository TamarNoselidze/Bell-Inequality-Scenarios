from qutip import *
import numpy as np


def rand_complex(dim): # random complex matrix
    return np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)


def random_observable():   # generate a random observable by random vector * bloch ops
    v = np.random.randn(3)
    v /= np.linalg.norm(v)  # normalize

    sx = sigmax()
    sy = sigmay()
    sz = sigmaz()

    return v[0]*sx + v[1]*sy + v[2]*sz



def generate_psi(state_type):
    # Alice/Charlie qubits
    ket_0 = basis(2,0)
    ket_1 = basis(2,1)

    # Bob's 2-qubit embedded basis states: |0> -> |00>, |1> -> |10>
    ket_0_B = tensor(ket_0, ket_0)
    ket_1_B = tensor(ket_1, ket_0)
    if state_type == 'ghz':
        # |GHZ(alpha)> = sqrt(alpha)|0>|00>|0> + sqrt(1-alpha)|1>|10>|1> ---- do we need this??
        # |GHZ> = 1/sqrt(2)|0>|00>|0> + 1/sqrt(2)|1>|10>|1>
        psi = 1/np.sqrt(2)*(tensor(ket_0, ket_0_B, ket_0) + tensor(ket_1, ket_1_B, ket_1))
        
    else: ## 'W'
        # |W> = 1/sqrt(3) * (|1>|00>|0> + |0>|10>|0> + |0>|00>|1>)
        psi = 1/np.sqrt(3)*(tensor(ket_1, ket_0_B, ket_0) + 
                            tensor(ket_0, ket_1_B, ket_0) + 
                            tensor(ket_0, ket_0_B, ket_1))
    
    return psi


def generate_qstate(w, state_type='ghz'):
    psi = generate_psi(state_type)
    rho_ent = ket2dm(psi)  # |psi><psi| density matrix

    ket_0 = basis(2, 0)
    I2 = qeye(2)

    # I/2 on Alice, I/2 on Bob_1, |0><0| on Bob_2, I/2 on Charlie
    noise = tensor(I2 / 2, I2 / 2, ket2dm(ket_0), I2 / 2)
    qstate = w*rho_ent + (1-w)*noise

    U_B = rand_unitary(4)
    U_full = tensor(I2, U_B, I2)
    
    U_full.dims = qstate.dims  # U_full should be [[2, 2, 2, 2], [2, 2, 2, 2]]
    
    return U_full * qstate * U_full.dag()



def update_observable(M, dim=2):
    # Enforce Hermiticity remove 1e-17 floating-point artifacts
    M_herm = 0.5 * (M + M.dag())
    vals, vecs = np.linalg.eigh(M_herm.full())

    # vals sorted ascending by eigenvalues, force lower -> -1, upper -> +1
    proj_minus = np.outer(vecs[:, 0], vecs[:, 0].conj())
    proj_plus  = np.outer(vecs[:, 1], vecs[:, 1].conj())

    observable = proj_plus - proj_minus
    return Qobj(observable)


def updated_qstate(op, qstate, A0, A1, X0, X2, Y1, C0, C1):
    I2 = qeye(2)
    ops = [I2, I2, I2, I2]  # [Alice, Bob_1, Bob_2, Charlie]

    # Alice (Slot 0)
    if 'A0' in op:
        ops[0] = A0
    elif 'A1' in op:
        ops[0] = A1

    # Bob Virtual 1 (Slot 1)
    if 'B0' in op:
        ops[1] = X0
    elif 'B2' in op:
        ops[1] = X2

    # Bob Virtual 2 (Slot 2)
    if 'B1' in op:
        ops[2] = Y1

    # Charlie (Slot 3)
    if 'C0' in op:
        ops[3] = C0
    elif 'C1' in op:
        ops[3] = C1


    full_op = tensor(ops)
    return (qstate * full_op).tr()


def evaluate_inequality(qstate, inequality, A0, A1, X0, X2, Y1, C0, C1):    #inequality given as [(operator, coefficient)]
    val = 0.0

    for (op, coeff) in inequality:
        val += coeff * updated_qstate(op, qstate, A0, A1, X0, X2, Y1, C0, C1)

    return np.real(val)



def get_environment_matrix(target_obs_name, target_slot, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1):
    I2 = qeye(2)
    M = Qobj(np.zeros((2, 2)), dims=[[2], [2]])

    for op, coeff in inequality:
        if target_obs_name in op:
            ops = [I2, I2, I2, I2]

            # Alice (Slot 0)
            if 'A0' in op: ops[0] = A0
            elif 'A1' in op: ops[0] = A1

            # Bob v1 (Slot 1)
            if 'B0' in op: ops[1] = X0
            elif 'B2' in op: ops[1] = X2

            # Bob v2 (Slot 2)
            if 'B1' in op: ops[2] = Y1

            # Charlie (Slot 3)
            if 'C0' in op: ops[3] = C0
            elif 'C1' in op: ops[3] = C1

            # Replace target observable with identity
            ops[target_slot] = I2

            full_op = tensor(ops)
            # Trace out the other 3 subsystems, keeping only target_slot
            M += coeff * (full_op * qstate).ptrace(target_slot)

    return M


def run_seesaw(inequality, state_type, w, num_seeds=500, tolerance=1e-6, verbose=False):
    I2 = qeye(2)
    global_max_violation = 0.0

    for _ in range(num_seeds):
        tolerance = 1e-6

        qstate = generate_qstate(w, state_type)
        A0 = random_observable()
        A1 = random_observable()
        X0 = random_observable()
        X2 = random_observable()
        Y1 = random_observable()
        C0 = random_observable()
        C1 = random_observable()


        current_score = evaluate_inequality(qstate, inequality, A0, A1, X0, X2, Y1, C0, C1)
  
        print("Initial score =", current_score)
        previous_score = -10.0

        iteration = 0
        # See-saw loop
        while abs(current_score - previous_score) > tolerance:
            iteration += 1
            previous_score = current_score

            # --- 1. OPTIMIZE ALICE (Target slot = 0) ---
            M_A0 = get_environment_matrix('A0', 0, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            A0 = update_observable(M_A0)
            M_A1 = get_environment_matrix('A1', 0, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            A1 = update_observable(M_A1)

            # --- 2. OPTIMIZE BOB VIRTUAL 1 (Target slot = 1) ---
            M_X0 = get_environment_matrix('B0', 1, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            X0 = update_observable(M_X0)

            M_X2 = get_environment_matrix('B2', 1, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            X2 = update_observable(M_X2)

            # --- 3. OPTIMIZE BOB VIRTUAL 2 (Target slot = 2) ---
            M_Y1 = get_environment_matrix('B1', 2, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            Y1 = update_observable(M_Y1)

            # --- 4. OPTIMIZE CHARLIE (Target slot = 3) ---
            M_C0 = get_environment_matrix('C0', 3, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            C0 = update_observable(M_C0)

            M_C1 = get_environment_matrix('C1', 3, inequality, qstate, A0, A1, X0, X2, Y1, C0, C1)
            C1 = update_observable(M_C1)          
            
            current_score = evaluate_inequality(qstate, inequality, A0, A1, X0, X2, Y1, C0, C1)
            print(iteration, current_score)

        if current_score > global_max_violation:
            global_max_violation = current_score
  
    print(f"For parameter w={w}, best found violation is: {global_max_violation:.5f}")
    print(f"Converged to this score in {iteration} iterations.")

    return global_max_violation




if __name__ == "__main__":
    CORRELATOR_NAMES = [
        'A0', 'A1', 'B0', 'B1', 'B2', 'C0', 'C1',
        'B0B1', 'B1B2', 'A0B0', 'A0B1', 'A0B2', 'A1B0', 'A1B1', 'A1B2',
        'B0C0', 'B1C0', 'B2C0', 'B0C1', 'B1C1', 'B2C1',
        'A0C0', 'A0C1', 'A1C0', 'A1C1',
        'A0B0C0', 'A0B0C1', 'A0B1C0', 'A0B1C1', 'A0B2C0', 'A0B2C1',
        'A1B0C0', 'A1B0C1', 'A1B1C0', 'A1B1C1', 'A1B2C0', 'A1B2C1',
        'A0B0B1', 'A1B0B1', 'A0B1B2', 'A1B1B2',
        'B0B1C0', 'B0B1C1', 'B1B2C0', 'B1B2C1',
        'A0B0B1C0', 'A0B0B1C1', 'A0B1B2C0', 'A0B1B2C1',
        'A1B0B1C0', 'A1B0B1C1', 'A1B1B2C0', 'A1B1B2C1'
    ]

    raw_ineqs = np.load("bell_inequalities_53D.npy")
    # Extract the 42 unique inequalities
    unique_ineqs = np.unique(np.round(raw_ineqs, 6), axis=0)

    # Convert all 42 inequalities to [(op, coeff), ...]
    all_inequalities = [
        [(name, ineq[i]) for i, name in enumerate(CORRELATOR_NAMES) if abs(ineq[i]) > 1e-6]
        for ineq in unique_ineqs
    ]

    state = 'ghz'
    w = 0.7  
    seeds = 10        # 10 random seeds per inequality
    print(f"Testing {len(all_inequalities)} genuine Bell inequalities for {state.upper()} state at w={w}...\n")

    results = []
    for idx, ineq in enumerate(all_inequalities):
        num_terms = len(ineq)
        score = run_seesaw(ineq, state_type=state, w=w, num_seeds=seeds, verbose=False)
        is_violated = score > 1.000001   #is this a good fix?
        results.append((idx + 1, num_terms, score, is_violated))
        
        status = "VIOLATED! ***" if is_violated else "No violation"
        print(f"Inequality #{idx + 1:2d} ({num_terms:2d} terms) -> Max Score: {score:.5f} [{status}]")


    # --- Print Summary Table ---
    print("\n" + "=" * 55)
    print(f"{'Ineq #':<8} {'Terms':<8} {'Score (w={w})':<18} {'Violated?':<12}")
    print("=" * 55)
    for ineq_num, terms, score, violated in results:
        v_str = "YES" if violated else "No"
        print(f"{ineq_num:<8} {terms:<8} {score:<18.5f} {v_str:<12}")
    print("=" * 55)
    violated_count = sum(1 for r in results if r[3])
    print(f"\nTotal violated: {violated_count} / {len(all_inequalities)}")

  