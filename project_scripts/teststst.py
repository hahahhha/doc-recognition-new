from itertools import product


for x in product([0, 1, 2], repeat=3):
    print(x)