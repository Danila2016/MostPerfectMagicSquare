#!/usr/bin/env python3

from itertools import permutations
from copy import deepcopy

rows = []  # текущие первые строки
solutions = []  # найденные решения для текущей подзадачи в текущем worker'е
squares = None  # список массивов 2x2, задающих квадраты
diag1 = []  # суммы главной диагонали квадратов 
diag2 = []  # суммы побочной диагонали квадратов
set_row_variants = None  # множество кортежей вариантов строк (i,j,k,t)


def init():
    """ Повторная инициализация в каждом worker'е """

    global set_row_variants, squares, solutions, diag1, diag2
    
    squares = ["28 21 38 43", "55 58 9 8", "37 44 27 22", "39 42 25 24",
                "48 33 18 31", "17 32 47 34", "12 5 54 59", "1 16 63 50",
                "53 60 11 6", "19 30 45 36", "62 51 4 13", "46 35 20 29",
                "3 14 61 52", "64 49 2 15", "10 7 56 57", "26 23 40 41"]

    for i in range(len(squares)):
        x = list(map(int, squares[i].split()))
        squares[i] = [x[:2], x[2:]]
        diag1.append(squares[i][0][0] + squares[i][1][1])
        diag2.append(squares[i][1][0] + squares[i][0][1])

    row_variants = []
    for i in range(16):
        for j in range(i+1, 16):
            for k in range(j+1, 16):
                for t in range(k+1, 16):
                    if sum(squares[ii][0][0] + squares[ii][0][1] for ii in [i, j, k, t]) == 260 and \
                    sum(squares[ii][1][0] + squares[ii][1][1] for ii in [i, j, k, t]) == 260:
                        row_variants.append((i, j, k, t))
    print(len(row_variants))
    set_row_variants = set(row_variants)


def solve_brute(row, c1, c2, c3, c4):
    """ Для текущих первых строк rows рекурсивно перебираем все варианты порядка расположения оставшихся значений
    в столбцах (их список - c1, c2, c3, c4 для каждого столбца) """

    global rows, set_row_variants, squares, solutions, diag1, diag2

    rows.append(row)

    if len(rows) == 4:
        # Проверяем суммы диагоналей для всех возможных перестановок столбцов
        for p in permutations(range(4)):
            d1 = 0
            d2 = 0
            for i in range(4):
                d1 += diag1[rows[i][p[i]]]
            if d1 == 260:
                for i in range(4):
                    d2 += diag2[rows[i][p[3-i]]]
                if d2 == 260:
                    cur_rows = [[r[i] for i in p] for r in rows]
                    solutions.append(tuple(cur_rows))
            
        rows.pop()
        return
    
    i, j, k, t = row

    c1_orig = c1[:]
    c2_orig = c2[:]
    c3_orig = c3[:]
    c4_orig = c4[:]

    c1.remove(i)
    c2.remove(j)
    c3.remove(k)
    c4.remove(t)
    for i in c1:
        for j in c2:
            for k in c3:
                for t in c4:
                    if tuple(sorted((i, j, k, t))) in set_row_variants:
                        solve_brute((i, j, k, t), c1, c2, c3, c4)
                    
    rows.pop()
    c1[:] = c1_orig
    c2[:] = c2_orig
    c3[:] = c3_orig
    c4[:] = c4_orig

def start_worker(task_queue, result_queue):
    """ Запуск одного работника """

    global solutions

    init()

    while True:
        row, c1, c2, c3, c4 = task_queue.get()
        if row is None:  # в случае признака завершения, сообщаем о завершении и завершаемся
            result_queue.put(None)
            return
        
        solve_brute(row, c1, c2, c3, c4)
        result_queue.put(solutions)
        solutions.clear()
