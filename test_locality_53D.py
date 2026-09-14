import itertools

# <A0>
# <A1>
# <B0>
# <B1>
# <B2>
# <C0>
# <C1>

# <B0B1>                   x8
# <B1B2>                   x9
# <A0B0>                   x10
# <A0B1>                   x11
# <A0B2>                   x12
# <A1B0>                   x13
# <A1B1>                   x14
# <A1B2>                   x15
# <B0C0>                   x16
# <B1C0>                   x17
# <B2C0>                   x18
# <B0C1>                   x19
# <B1C1>                   x20
# <B2C1>                   x21
# <A0C0>                   x22
# <A0C1>                   x23
# <A1C0>                   x24
# <A1C1>                   x25


# <A0B0C0>                 x26  
# <A0B0C1>                 x27
# <A0B1C0>                 x28
# <A0B1C1>                 x29
# <A0B2C0>                 x30
# <A0B2C1>                 x31
# <A1B0C0>                 x32
# <A1B0C1>                 x33
# <A1B1C0>                 x34
# <A1B1C1>                 x35
# <A1B2C0>                 x36
# <A1B2C1>                 x37


# <A0B0B1>                 x38
# <A1B0B1>                 x39
# <A0B1B2>                 x40
# <A1B1B2>                 x41
# <B0B1C0>                 x42
# <B0B1C1>                 x43
# <B1B2C0>                 x44
# <B1B2C1>                 x45


# <A0B0B1C0>               x46
# <A0B0B1C1>               x47
# <A0B1B2C0>               x48
# <A0B1B2C1>               x49
# <A1B0B1C0>               x50
# <A1B0B1C1>               x51
# <A1B1B2C0>               x52
# <A1B1B2C1>               x53




# a0, a1, c0, c1, b0, b1, b2
deterministic_strategies = list(itertools.product([-1, 1], repeat=7))
local_vertices = []

for strategy in deterministic_strategies:
    a0, a1, b0, b1, b2,  c0, c1 = strategy

    base_variables = {'A0' : a0, 'A1' : a1, 'B0' : b0, 'B1' : b1, 'B2' : b2, 'C0' : c0, 'C1' : c1 }

    joint_variables = [
                    #  'A0', 'A1', 'B0', 'B1', 'B2', 'C0', 'C1',
                     'B0 B1', 'B1 B2', 'A0 B0', 'A0 B1', 'A0 B2', 'A1 B0', 'A1 B1', 'A1 B2', 'B0 C0', 'B1 C0', 'B2 C0', 'B0 C1', 'B1 C1', 'B2 C1', 'A0 C0', 'A0 C1', 'A1 C0', 'A1 C1',
                     'A0 B0 C0', 'A0 B0 C1', 'A0 B1 C0', 'A0 B1 C1', 'A0 B2 C0', 'A0 B2 C1', 'A1 B0 C0', 'A1 B0 C1', 'A1 B1 C0', 'A1 B1 C1', 'A1 B2 C0', 'A1 B2 C1', 'A0 B0 B1', 'A1 B0 B1', 'A0 B1 B2', 'A1 B1 B2', 'B0 B1 C0', 'B0 B1 C1', 'B1 B2 C0', 'B1 B2 C1',
                     'A0 B0 B1 C0', 'A0 B0 B1 C1', 'A0 B1 B2 C0', 'A0 B1 B2 C1', 'A1 B0 B1 C0', 'A1 B0 B1 C1', 'A1 B1 B2 C0', 'A1 B1 B2 C1' 
                    ]


    vector = [a0, a1, c0, c1, b0, b1, b2]
    for v in joint_variables:
        v_elements = v.split(' ')

        joint_value = 1
        for val in v_elements:
            joint_value *= base_variables[val]

        vector.append(joint_value)


    local_vertices.append(vector)

# print(len(local_vertices[0]))



import cvxpy as cp
import numpy as np



def test_behaviour(b_target):
    V = np.array(local_vertices).T  

    p = cp.Variable(128, nonneg=True)   # Condition 2: p_i >= 0 is handled by nonneg=True

    constraints = [
        V @ p == b_target,  # Condition 1: sum(p_i * v_i) = b_target
        cp.sum(p) == 1      # Condition 3: sum(p_i) = 1
    ]

    objective = cp.Minimize(0)  # a dummy objective

    problem = cp.Problem(objective, constraints)
    problem.solve()

    if problem.status == cp.OPTIMAL:
        print("Result: LOCAL")
        print("The behavior can be simulated by classical deterministic strategies.")
        # specific weights with: print(np.round(p.value, 4))

    elif problem.status in [cp.INFEASIBLE, cp.INFEASIBLE_INACCURATE]:
        print("Result: NON-LOCAL")
        print("No classical convex combination exists. This behavior violates a Bell inequality.")

    else:
        print(f"Solver failed. Status: {problem.status}")   



b = np.ones(53)
test_behaviour(b)