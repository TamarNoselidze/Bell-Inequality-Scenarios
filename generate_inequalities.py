# <A0>                     x1
# <A1>                     x2
# <B0>                     x3
# <B1>                     x4
# <B2>                     x5
# <B0B1>                   x6
# <B1B2>                   x7
# <A0B0>                   x8
# <A0B1>                   x9
# <A0B2>                   x10
# <A1B0>                   x11
# <A1B1>                   x12
# <A1B2>                   x13
# <A0B0B1>                 x14
# <A1B0B1>                 x15
# <A0B1B2>                 x16
# <A1B1B2>                 x17

import itertools

def sign(e):
    x = (-1)**(e+1)
    return '-' if x < 0 else '+'


contexts = [
    # Alice 0 (x1) with Bob {0, 1}
    {'A': 1, 'B0': 3, 'B1': 4, 'AB0': 8,  'AB1': 9,  'B0B1': 6, 'AB0B1': 14},
    
    # Alice 0 (x1) with Bob {1, 2}
    {'A': 1, 'B0': 4, 'B1': 5, 'AB0': 9,  'AB1': 10, 'B0B1': 7, 'AB0B1': 16},
    
    # Alice 1 (x2) with Bob {0, 1}
    {'A': 2, 'B0': 3, 'B1': 4, 'AB0': 11, 'AB1': 12, 'B0B1': 6, 'AB0B1': 15},
    
    # Alice 1 (x2) with Bob {1, 2}
    {'A': 2, 'B0': 4, 'B1': 5, 'AB0': 12, 'AB1': 13, 'B0B1': 7, 'AB0B1': 17}
]

def generate_inequality(a, b0, b1, ctx):
    terms = [
        f"{sign(a)}x{ctx['A']}",
        f"{sign(b0)}x{ctx['B0']}",
        f"{sign(b1)}x{ctx['B1']}",
        f"{sign(a+b0)}x{ctx['AB0']}",
        f"{sign(a+b1)}x{ctx['AB1']}",
        f"{sign(b0+b1)}x{ctx['B0B1']}",
        f"{sign(a+b0+b1)}x{ctx['AB0B1']}"
    ]
    return " ".join(terms) + " <= 1"



def bob_only_inequalities(b0, b1, shift=0):   # old function for inequalities in 8D with only Bob's measurements
    inequality = f'{sign(b0)}x{3+shift} {sign(b1)}x{4+shift} {sign(b0+b1)}x{6+shift} <= 1'
    return inequality



# ----------------------------------------------------------------------------------------


outcomes = list(itertools.product([0, 1], repeat=3))
all_inequalities = []



### old inequalities only for Bob
b_values = list(itertools.product([0,1], repeat=2))

for b in b_values:
    all_inequalities.append(bob_only_inequalities(b[0], b[1]))

for b in b_values:
    all_inequalities.append(bob_only_inequalities(b[0], b[1], shift=1))



### new inequalities
for ctx in contexts:
    for a, b0, b1 in outcomes:
        all_inequalities.append(generate_inequality(a, b0, b1, ctx))



output_filename = "alice_bob_17D.ieq"
with open(output_filename, "w") as f:
    f.write("DIM = 17\n\n")
    f.write("VALID\n")
    f.write(" ".join(["0"] * 17) + "\n\n")
    f.write("INEQUALITIES_SECTION\n")
    for ieq in all_inequalities:
        f.write(ieq + "\n")
    f.write("\nEND\n\n")


