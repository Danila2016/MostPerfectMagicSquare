#!/usr/bin/env python3

from tqdm import tqdm
from itertools import permutations
from copy import deepcopy

from multiprocessing import Manager, Process, Pool
from p3_worker import start_worker

NUM_WORKERS = 12  # количество параллельных процессов (>= 3)

set_row_variants = None
squares = None

def profile(f):
    return f

def tqdm(x):
    return x

@profile
def main():
    global set_row_variants, squares
    
    squares = ["28 21 38 43", "55 58 9 8", "37 44 27 22", "39 42 25 24",
                "48 33 18 31", "17 32 47 34", "12 5 54 59", "1 16 63 50",
                "53 60 11 6", "19 30 45 36", "62 51 4 13", "46 35 20 29",
                "3 14 61 52", "64 49 2 15", "10 7 56 57", "26 23 40 41"]

    for i in range(len(squares)):
        x = list(map(int, squares[i].split()))
        squares[i] = [x[:2], x[2:]]

    # Ищем все варианты из 4 квадратов, которые могут составлять строку
    row_variants = []
    for i in range(16):
        for j in range(i+1, 16):
            for k in range(j+1, 16):
                for t in range(k+1, 16):
                    if sum(squares[ii][0][0] + squares[ii][0][1] for ii in [i, j, k, t]) == 260 and \
                    sum(squares[ii][1][0] + squares[ii][1][1] for ii in [i, j, k, t]) == 260:
                        row_variants.append((i, j, k, t))
    print("Вариантов строк:", len(row_variants))
    set_row_variants = set(row_variants)

    # Ищем все варианты из 4 квадратов, которые могут составлять столбец
    pow = [2**i for i in range(17)]
    col_variants = []
    bin_col_variants = []  # битовые маски квадратов столбца
    for i in range(16):
        for j in range(i+1, 16):
            for k in range(j+1, 16):
                for t in range(k+1, 16):
                    if sum(squares[ii][0][0] + squares[ii][1][0] for ii in [i, j, k, t]) == 260 and \
                    sum(squares[ii][0][1] + squares[ii][1][1] for ii in [i, j, k, t]) == 260:
                        col_variants.append((i, j, k, t))
                        bin_col_variants.append(pow[i+1] + pow[j+1] + pow[k+1] + pow[t+1])
    print("Вариантов столбцов:", len(col_variants))

    # Ищем все пары столбцов, которые включают квадраты с индексами a и b, a < b
    col_pairs = [[[] for j in range(16)] for i in range(16)]
    for i in range(len(col_variants)):
        for j in range(i+1, len(col_variants)):
            if len(set(col_variants[i]+col_variants[j])) == 8:
                for a in col_variants[i]:
                    for b in col_variants[j]:
                        if a > b:
                            i_, j_ = j, i
                            a_, b_ = b, a
                        else:
                            a_, b_ = a, b
                            i_, j_ = i, j
                        col_pairs[a_][b_].append((col_variants[i_], col_variants[j_], bin_col_variants[i_], bin_col_variants[j_]))
    #print(list(map(len, col_pairs)))

    # Подготовка для распараллеливания
    manager = Manager()
    task_queue = manager.Queue()  # task queue
    result_queue = manager.Queue()  # result queue

    np = NUM_WORKERS - 2
    processes = []
    for i in range(np):
        p = Process(target=start_worker, args=(task_queue, result_queue))
        p.start()
        processes.append(p)

    p_saver = Process(target=saver, args=(np, result_queue))
    p_saver.start()

    # Перебираем все варианты первой строки и выбираем четвёрки столбцов, которые могут быть выбраны
    for i,j,k,t in tqdm(row_variants):
        print("Queue size:", task_queue.qsize())
        for c1, c2, b1, b2 in tqdm(col_pairs[i][j]):
            for c3, c4, b3, b4 in col_pairs[k][t]:
                if b1 & b3 == 0 and b2 & b3 == 0 and b1 & b4 == 0 and b2 & b4 == 0:
                    task_queue.put(((i,j,k,t), list(c1), list(c2), list(c3), list(c4)))

    # Признак завершения очереди - пустые значения
    for i in range(np):
        task_queue.put((None, None, None, None, None))


def saver(np, result_queue):
    """ Сохранение результатов по мере их поступления.
    Результаты сохраняются в виде индексов квадратов (0-15, по строкам), 4 бита на индекс, без разделителей. """
    n_solutions = 0
    next_report = 1000_000
    with open("result.bin", 'wb') as fw:
        while True:
            sol = result_queue.get()
            if sol is None:  # Отслеживаем признак завершения в очереди результатов
                np -= 1
                if np == 0:
                    break
            else:
                n_solutions += len(sol)
                if n_solutions >= next_report:
                    print(n_solutions)
                    while next_report <= n_solutions:
                        next_report += 1000_000
                for s in sol:
                    for a, b, c, d in s:  # a,b,c,d - одна строка
                        #print(a,b,c,d)
                        fw.write((a*16 + b).to_bytes(1, 'big', signed=False))
                        fw.write((c*16 + d).to_bytes(1, 'big', signed=False))
                
                fw.flush()
            
    print("Total:", n_solutions)

if __name__ == '__main__':
    main()
