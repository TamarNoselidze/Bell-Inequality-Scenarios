import itertools
import cdd

alice_strategies = list(itertools.product([1, -1], repeat=2))
# print(alice_strategies)

bob_non_contextual_strategies = list(itertools.product([1, -1], repeat=4))
# print(bob_non_contextual_strategies)

def is_valid_pr_box(values):
    return (values[0] * values[1] * values[2] * values[3]) == -1

bob_contextual_strategies = [b for b in itertools.product([1, -1], repeat=4) if is_valid_pr_box(b)]

bob_strategies = bob_non_contextual_strategies + bob_contextual_strategies



def create_26D_vector(a_strat, b_strat, is_pr_box=False):
    a0, a1 = a_strat
    b0, b1, b2, b3 = b_strat

    b01, b12, b23, b30 = a0*b0, a0*b1, a0*b2, a0*b3
    
    # If it's a PR-box strategy, individual Bs are 0
    if is_pr_box:
        b0, b1, b2, b3 = 0, 0, 0, 0
        b01, b12, b23, b30 = b_strat

    # Calculate all 26 terms in the exact order of Table 1

    # [
        # A_0  A_1 
        # B_0  B_1  B_2 B_3  
        # A_0|B_0  A_0|B_1  A_0|B_2  A_0|B_3  A_1|B_0  A_1|B_1  A_1|B_2  A_1|B_3  
        # B_0|B_1  B_1|B_2  B_2|B_3  B_3|B_0 
        # A_0|B_0|B_1  A_0|B_1|B_2  A_0|B_2|B_3  A_0|B_3|B_0  A_1|B_0|B_1  A_1|B_1|B_2  A_1|B_2|B_3  A_1|B_3|B_0 
    #]

    vector = [
        a0, a1,                      # <Ax>
        b0, b1, b2, b3,              # <By>
        a0*b0, a0*b1, a0*b2, a0*b3,                a1*b0, a1*b1, a1*b2, a1*b3,    # <AxBy>
        b01, b12, b23, b30,  # <By1By2>
        a0*b0*b1, a0*b1*b2, a0*b2*b3, a0*b3*b0,    a1*b0*b1, a1*b1*b2, a1*b2*b3, a1*b3*b0  # <AxBy1By2>
    ]
    return vector


nc_vectors = [create_26D_vector(a, b) for a in alice_strategies for b in bob_non_contextual_strategies]
c_vectors = [create_26D_vector(a, b, is_pr_box=True) for a in alice_strategies for b in bob_contextual_strategies]

all_vectors = nc_vectors + c_vectors


### printing the .poi file

# DIM = 26

# CONV_SECTION
# 1  1  -1  1  0  ... (26 numbers for Joint Corner 1)
# 1  1   1 -1  0  ... (26 numbers for Joint Corner 2)
# ...
# ... (All 96 rows go here)
# ...
# -1 -1  0  0  1  ... (26 numbers for Joint Corner 96)

# END


with open('26D_old.poi', 'w') as output_file:
    output_file.write("DIM = 26\n")
    output_file.write("CONV_SECTION\n")

    for i in range(96):
        vector = all_vectors[i]
        vector_string = "  ".join(str(v) for v in vector)
        # vector_string += f' (26 numbers for Joint Corner {i+1})\n'
        output_file.write(vector_string+'\n')
    output_file.write("\nEND\n")






# cdd_format_vectors = [[1] + list(vec) for vec in all_vectors]
# # 2. Load the matrix into CDD
# # We use 'fraction' to avoid floating-point rounding errors in 26 dimensions!
# mat = cdd.Matrix(cdd_format_vectors, number_type='fraction')
# mat.rep_type = cdd.RepType.GENERATOR

# # 3. Build the Polyhedron
# print("Crunching the 26-dimensional hull (this might take a minute)...")
# poly = cdd.Polyhedron(mat)

# # 4. Get the H-representation (The Inequalities!)
# inequalities = poly.get_inequalities()

# print(f"Found {inequalities.row_size} inequalities/facets.")

# # 5. Print a few out to see them
# for i in range(min(5, inequalities.row_size)):
#     print(inequalities[i])








# import json
# import cdd.gmp  

# # 1. Build CDD-format vectors: [1, v1, v2, ...]
# cdd_format_vectors = [[1] + list(vec) for vec in all_vectors]

# # 2. Load the matrix using the new factory function
# mat = cdd.gmp.matrix_from_array(cdd_format_vectors, rep_type=cdd.gmp.RepType.GENERATOR)

# # 3. Build the Polyhedron
# print("Crunching the 26-dimensional hull (this might take a minute)...")
# poly = cdd.gmp.polyhedron_from_matrix(mat)


# # 4. Get the H-representation (CORRECTED METHOD)
# inequalities = poly.get_inequalities()

# print(f"Found {inequalities.row_size} inequalities/facets.")

# # 5. Backup the result to disk so you don't have to recompute!
# # Convert GMP rationals to strings to preserve exact arithmetic and allow JSON serialization
# ineq_data = []
# for i in range(inequalities.row_size):
#     row_strings = [str(val) for val in inequalities[i]]
#     ineq_data.append(row_strings)

# with open("26d_hull_inequalities.json", "w") as f:
#     json.dump(ineq_data, f)
# print("Saved exact inequalities to '26d_hull_inequalities.json'.")


# # 6. Print a few
# for i in range(min(5, inequalities.row_size)):
#     print(inequalities[i])