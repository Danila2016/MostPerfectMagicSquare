#!/usr/bin/env python3

squares = ["28 21 38 43", "55 58 9 8", "37 44 27 22", "39 42 25 24",
                "48 33 18 31", "17 32 47 34", "12 5 54 59", "1 16 63 50",
                "53 60 11 6", "19 30 45 36", "62 51 4 13", "46 35 20 29",
                "3 14 61 52", "64 49 2 15", "10 7 56 57", "26 23 40 41"]

for i in range(len(squares)):
    x = list(map(int, squares[i].split()))
    squares[i] = [x[:2], x[2:]]

with open("result.bin", 'rb') as f:
    solution = []
    solution_bin_set = set([])
    solution_bin = []
    for x in f.read():
        solution_bin += [chr(x)]
        solution += [x // 16, x % 16]
        if len(solution) == 16:
            if "".join(solution_bin) in solution_bin_set:
                assert(False)
            solution_bin_set.add("".join(solution_bin))
            assert(set(solution) == set(range(16)))
            solution = [[solution[i*4 + j] for j in range(4)] for i in range(4)]

            sq = [[None]*8 for i in range(8)]
            for i in range(4):
                for j in range(4):
                    for k in range(2):
                        for t in range(2):
                            sq[2*i+k][2*j+t] = squares[solution[i][j]][k][t]

            for i in range(8):
                assert(sum(sq[i]) == 260)
                assert(sum(sq[j][i] for j in range(8)) == 260)
            assert(sum(sq[j][j] for j in range(8)) == 260)
            assert(sum(sq[j][7-j] for j in range(8)) == 260)

            solution.clear()
            solution_bin.clear()

            if len(solution_bin_set) % 1000_000 == 0:
                print(len(solution_bin_set))
            
    assert(solution == [])

    print("Unique solutions:", len(solution_bin_set))
            