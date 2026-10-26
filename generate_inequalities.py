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


import itertools

var_map = {
    'A0': 1, 'A1': 2, 'B0': 3, 'B1': 4, 'B2': 5, 'C0': 6, 'C1': 7,
    'B0B1': 8, 'B1B2': 9,
    'A0B0': 10, 'A0B1': 11, 'A0B2': 12, 'A1B0': 13, 'A1B1': 14, 'A1B2': 15,
    'B0C0': 16, 'B1C0': 17, 'B2C0': 18, 'B0C1': 19, 'B1C1': 20, 'B2C1': 21,
    'A0C0': 22, 'A0C1': 23, 'A1C0': 24, 'A1C1': 25,
    'A0B0C0': 26, 'A0B0C1': 27, 'A0B1C0': 28, 'A0B1C1': 29, 'A0B2C0': 30, 'A0B2C1': 31,
    'A1B0C0': 32, 'A1B0C1': 33, 'A1B1C0': 34, 'A1B1C1': 35, 'A1B2C0': 36, 'A1B2C1': 37,
    'A0B0B1': 38, 'A1B0B1': 39, 'A0B1B2': 40, 'A1B1B2': 41,
    'B0B1C0': 42, 'B0B1C1': 43, 'B1B2C0': 44, 'B1B2C1': 45,
    'A0B0B1C0': 46, 'A0B0B1C1': 47, 'A0B1B2C0': 48, 'A0B1B2C1': 49,
    'A1B0B1C0': 50, 'A1B0B1C1': 51, 'A1B1B2C0': 52, 'A1B1B2C1': 53
}


def sign(e):
    # If (-1)^(e+1) is negative, we have a minus sign
    return '-' if (-1)**(e+1) < 0 else '+'

def generate_4body_inequality(a_val, bi_val, bj_val, c_val, A, Bi, Bj, C):

    terms = [
        f"{sign(a_val)}x{var_map[A]}",
        f"{sign(bi_val)}x{var_map[Bi]}",
        f"{sign(bj_val)}x{var_map[Bj]}",
        f"{sign(c_val)}x{var_map[C]}",
        
        f"{sign(bi_val+bj_val)}x{var_map[Bi+Bj]}",
        
        f"{sign(a_val+bi_val)}x{var_map[A+Bi]}",
        f"{sign(a_val+bj_val)}x{var_map[A+Bj]}",
        f"{sign(a_val+c_val)}x{var_map[A+C]}",
        f"{sign(bi_val+c_val)}x{var_map[Bi+C]}",
        f"{sign(bj_val+c_val)}x{var_map[Bj+C]}",
        
        f"{sign(a_val+bi_val+bj_val)}x{var_map[A+Bi+Bj]}",
        f"{sign(a_val+bi_val+c_val)}x{var_map[A+Bi+C]}",
        f"{sign(a_val+bj_val+c_val)}x{var_map[A+Bj+C]}",
        f"{sign(bi_val+bj_val+c_val)}x{var_map[Bi+Bj+C]}",
        
        f"{sign(a_val+bi_val+bj_val+c_val)}x{var_map[A+Bi+Bj+C]}"
    ]
    return " ".join(terms) + " <= 1"


# Iterate through all measurement contexts and outcome combinations
outcomes = list(itertools.product([0, 1], repeat=4))


alice_options = ['A0', 'A1']
bob_contexts = [('B0', 'B1'), ('B1', 'B2')] # Bob's two compatible contexts
charlie_options = ['C0', 'C1']

all_inequalities = []

for A in alice_options:
    for Bi, Bj in bob_contexts:
        for C in charlie_options:

            for a_val, bi_val, bj_val, c_val in outcomes:
                ineq = generate_4body_inequality(a_val, bi_val, bj_val, c_val, A, Bi, Bj, C)
                all_inequalities.append(ineq)


# Write exactly to PORTA format
output_filename = "alice_bob_charlie_53D.ieq"

with open(output_filename, "w", newline='\n') as f:
    f.write("DIM = 53\n\nVALID\n")
    f.write(" ".join(["0"] * 53) + "\n\nINEQUALITIES_SECTION\n")
    for ieq in all_inequalities:
        f.write(ieq + "\n")
    f.write("\nEND\n\n")