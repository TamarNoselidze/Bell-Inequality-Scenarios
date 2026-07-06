from qutip import *
import numpy as np

import matplotlib.pyplot as plt

from qutip import *
import numpy as np
import scipy

def rand_complex(dim): # random complex matrix
    return np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)


def generate_random_POVMs(dim=2, num_outcomes=2):
    # M = [Qobj(np.random.rand(4, 4)) for _ in range(4)]
    M = [Qobj(rand_complex(dim)) for _ in range(num_outcomes)]    
    
    H = [M_i@M_i.dag() for M_i in M]

    S = sum(H)
    # print(S)

    S_inv_sqrt_mat = scipy.linalg.fractional_matrix_power(S.full(), -0.5)
    S_inv_sqrt = Qobj(S_inv_sqrt_mat)

    # normalize for the final POVM elements: E_i = S^(-1/2) * H_i * S^(-1/2)
    E = [S_inv_sqrt * H_i * S_inv_sqrt for H_i in H]
    return E


def random_observable():   # generate a random observable by random vector * bloch ops
    v = np.random.randn(3)
    v /= np.linalg.norm(v)  # normalize

    sx = sigmax()
    sy = sigmay()
    sz = sigmaz()

    return v[0]*sx + v[1]*sy + v[2]*sz

def generate_sigma(alpha, w):
    # Alice qubit
    ket_0_a = basis(2,0)
    ket_1_a = basis(2,1)

    # "virtual" Bob qubits (since we split original Bob and add "virtual" Bob and Charlie)
    ket_0_b = basis(2,0)
    ket_1_b = basis(2,1)

    # embedding to include additional Charlie!!
    # |0> -> |00>
    # |1> -> |10>

    ket_0_B = tensor(ket_0_b, ket_0_b)
    ket_1_B = tensor(ket_1_b, ket_0_b)

    psi = (np.sqrt(alpha)*tensor(ket_0_a, ket_1_B) +
           np.sqrt(1-alpha)*tensor(ket_1_a, ket_0_B))

    rho_ent = ket2dm(psi)  # |psi><psi| density matrix

    # noise = tensor(qeye(2), ket2dm(ket_0_B))   # I/4 but embedded
    noise = tensor(qeye(2)/2, ket2dm(ket_0_B))   # I/4 but embedded


    sigma = w*rho_ent + (1-w)*noise

    U_BC = rand_unitary(4)
    U_full = tensor(qeye(2), U_BC)
    
    U_full.dims = sigma.dims  # U_full should be [[2, 2, 2], [2, 2, 2]]
    
    return U_full * sigma * U_full.dag()



def term(coeff, op0, op1, op2, target_slot, sigma):  # coefficient (c_xy ^ab) * Partial Trace(sigma * op0 op1 op2)
    full_op = tensor(op0, op1, op2)
    # traced_out = (sigma * full_op).ptrace(target_slot)
    traced_out = (full_op * sigma).ptrace(target_slot)
    return coeff * traced_out


def update_povm(M, dim=2):   # build Q+ from positive eigenvectors of rho+ - rho-  (M)
    eigenvalues, eigenvectors = np.linalg.eigh(M.full())
    Q_plus_mat = np.zeros((dim, dim), dtype=complex)
    
    #   Sum outer products of eigenvectors that have a positive eigenvalue
    for val, vec in zip(eigenvalues, eigenvectors.T):
        if val > 0:
            Q_plus_mat += np.outer(vec, vec.conj())
            
    Q_plus = Qobj(Q_plus_mat)
    Q_minus = qeye(dim) - Q_plus
    return [Q_plus, Q_minus], (Q_plus - Q_minus)  # Returns new POVM list and Observable


def update_observable(M, dim=2):
    vals, vecs = np.linalg.eigh(M.full())

    # vals sorted ascending by eigenvalues, force lower -> -1, upper -> +1
    proj_minus = np.outer(vecs[:, 0], vecs[:, 0].conj())
    proj_plus  = np.outer(vecs[:, 1], vecs[:, 1].conj())

    observable = proj_plus - proj_minus
    return Qobj(observable)


def evaluate_inequality_15(qstate, A0, A1, B0, C1, C3):
    I2 = qeye(2)
    val = 0.0
    val += 2.0 * (qstate * tensor(I2, B0, I2)).tr()
    val += 1.0 * (qstate * tensor(A0, I2, C1)).tr()
    val += 1.0 * (qstate * tensor(A0, I2, C3)).tr()
    val += 1.0 * (qstate * tensor(A1, I2, C1)).tr()
    val -= 1.0 * (qstate * tensor(A1, I2, C3)).tr()
    val -= 1.0 * (qstate * tensor(A0, B0, C1)).tr()
    
    val -= 1.0 * (qstate * tensor(A0, B0, C3)).tr()
    # val -= 1.0 * (qstate * tensor(A0, C3, B0)).tr()

    val -= 1.0 * (qstate * tensor(A1, B0, C1)).tr()

    val += 1.0 * (qstate * tensor(A1, B0, C3)).tr()
    # val += 1.0 * (qstate * tensor(A1, C3, B0)).tr()

    return np.real(val)


def run_seesaw(alpha, w, num_seeds=10, tolerance=1e-6):
    I2 = qeye(2)
    global_max_violation = 0.0

    for _ in range(num_seeds):
        tolerance = 1e-6

        qstate = generate_sigma(alpha=alpha, w=w)
        # print("trace =", qstate.tr())
        # print("dims=", qstate.dims)
        # print(
        #     evaluate_inequality_15(
        #     qstate,
        #     qeye(2),
        #     qeye(2),
        #     qeye(2),
        #     qeye(2),
        #     qeye(2)
        #     )
        #     )

        # random 2D POVMs for the 3 parties
        # P_A = [generate_random_POVMs(dim=2) for _ in range(2)]  # A0, A1
        # P_B = [generate_random_POVMs(dim=2) for _ in range(2)]  # B0
        # P_C = [generate_random_POVMs(dim=2) for _ in range(2)]  # C1, C3

        # # Convert to initial Observables):
        # A0, A1 = (
        #     P_A[0][0] - P_A[0][1],
        #     P_A[1][0] - P_A[1][1],
        # )
        # B0 = P_B[0][0] - P_B[0][1]   # we skip B1 here
        # C1, C3 = (
        #     P_C[0][0] - P_C[0][1],
        #     P_C[1][0] - P_C[1][1],
        # )

        A0 = random_observable()
        A1 = random_observable()
        B0 = random_observable()
        C1 = random_observable()
        C3 = random_observable()


        current_score = evaluate_inequality_15(qstate, A0, A1, B0, C1, C3)
        print("Initial score =", current_score)
        previous_score = -10.0

        iteration = 0
        # See-saw loop
        while abs(current_score - previous_score) > tolerance:
            iteration += 1
            previous_score = current_score

            # --- OPTIMIZE ALICE (tracing out A0, A1 i.e. target dlot=0) ---
            rho_plus_A0 = term(1.0, I2, I2, C1, 0, qstate)
            rho_plus_A0 += term(1.0, I2, I2, C3, 0, qstate)
            rho_plus_A0 += term(-1.0, I2, B0, C1, 0, qstate)
            rho_plus_A0 += term(-1.0, I2, B0, C3, 0, qstate)
            print("A0:", rho_plus_A0.eigenenergies())
            # P_A[0], A0 = update_povm(2.0 * rho_plus_A0)
            A0 = update_observable(2.0 * rho_plus_A0)

            rho_plus_A1 = term(1.0, I2, I2, C1, 0, qstate)
            rho_plus_A1 += term(-1.0, I2, I2, C3, 0, qstate)
            rho_plus_A1 += term(-1.0, I2, B0, C1, 0, qstate)
            rho_plus_A1 += term(1.0, I2, B0, C3, 0, qstate)
            print("A1:", rho_plus_A1.eigenenergies())
            # P_A[1], A1 = update_povm(2.0 * rho_plus_A1)
            A1 = update_observable(2.0 * rho_plus_A1)



            # --- OPTIMIZE CHARLIE (tracing out C1, C3 i.e. target slot=2)
            rho_plus_C1 = term(1.0, A0, I2, I2, 2, qstate)
            rho_plus_C1 += term(1.0, A1, I2, I2, 2, qstate)
            rho_plus_C1 += term(-1.0, A0, B0, I2, 2, qstate)
            rho_plus_C1 += term(-1.0, A1, B0, I2, 2, qstate)
            print("C1:", rho_plus_C1.eigenenergies())
            # P_C[0], C1 = update_povm(2.0 * rho_plus_C1)
            C1 = update_observable(2.0 * rho_plus_C1)


            rho_plus_C3 = term(1.0, A0, I2, I2, 2, qstate)
            rho_plus_C3 += term(-1.0, A1, I2, I2, 2, qstate)
            rho_plus_C3 += term(-1.0, A0, B0, I2, 2, qstate)
            rho_plus_C3 += term(1.0, A1, B0, I2, 2, qstate)
            print("C3:", rho_plus_C3.eigenenergies())
            # P_C[1], C3 = update_povm(2.0 * rho_plus_C3)
            C3 = update_observable(2.0 * rho_plus_C3)

            # --- OPTIMIZE BOB (tracing out B0 i.e. target slot=1)
            rho_plus_B0 = term(2.0, I2, I2, I2, 1, qstate)
            rho_plus_B0 += term(-1.0, A0, I2, C1, 1, qstate)
            rho_plus_B0 += term(-1.0, A0, I2, C3, 1, qstate)
            rho_plus_B0 += term(-1.0, A1, I2, C1, 1, qstate)
            rho_plus_B0 += term(1.0, A1, I2, C3, 1, qstate)

            # P_B[0], B0 = update_povm(2.0 * rho_plus_B0)
            B0 = update_observable(2.0 * rho_plus_B0)

            print(B0.eigenenergies())
        

            current_score = evaluate_inequality_15(qstate, A0, A1, B0, C1, C3)
            print(iteration, current_score)
        # print(f"Seed {seed + 1} Converged Score: {current_score:.5f}")

        if current_score > global_max_violation:
            global_max_violation = current_score
  
    print(f"For w={w} and alpha={alpha}, best found violation: {global_max_violation:.5f}")

    return global_max_violation



# run_seesaw(alpha=0.5, w=1)     # 1 run of seesaw


# import numpy as np

# alphas = np.linspace(0.0, 1.0, 101)
# omegas = np.linspace(0.0, 1.0, 101)

# scores = np.zeros((len(alphas), len(omegas)))

# for i, alpha in enumerate(alphas):
#     print(f"alpha = {alpha:.2f}")

#     for j, w in enumerate(omegas):
#         scores[i, j] = run_seesaw(alpha=alpha, w=w)

# plot_different_values(alphas, omegas, scores)




def compute_critical_curve(alpha_values, w_values):

    critical_w = []

    for alpha in alpha_values:

        print(f"alpha = {alpha:.3f}")

        wc = np.nan

        for w in w_values:

            score = run_seesaw(alpha, w)

            if score > 2.0:
                wc = w
                break

        critical_w.append(wc)

    return np.array(critical_w)


alphas = np.linspace(0.5,1.0,26)
weights = np.linspace(0.0,1.0,201)

critical = compute_critical_curve(alphas, weights)

plt.figure(figsize=(7,5))

plt.plot(
    alphas,
    critical,
    'ro-',
    label="Inequality (15)"
)

plt.xlabel(r"$\alpha$")
plt.ylabel(r"$w_c$")
plt.title("Critical visibility for inequality (15)")
plt.grid(True)
plt.legend()

plt.show()