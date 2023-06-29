import os
import argparse

from distutils.util import strtobool

def pos_int(value):
    pos_i = int(value)
    if pos_i < 1:
        msg = "Valor recebido %s. Tente um valor > 0!" % value
        raise argparse.ArgumentTypeError(msg)
    return pos_i

def valid_file(file):
    if not os.path.exists(file):
        msg = "Valor recebido %s. Arquivo nao existe!" % file
        raise argparse.ArgumentTypeError(msg)
    return file

def valid_bool(b):
    return bool(strtobool(b))

def read_sudokus(file):
    sudokus = []
    with open(file) as file:
        sudokus = [[[int(e) for e in line] for line in sudoku.split("\n")] for sudoku in file.read().split("\n\n")]
    return sudokus

def get_rows(sudoku):
    return [[f"L{i + 1}", *line] for i, line in enumerate(sudoku)]

def get_columns(sudoku):
    t = [[sudoku[l][c] for l in range(9)] for c in range(9)]
    return [[f"C{i + 1}", *col] for i, col in enumerate(t)]

def get_regions(sudoku):
    regions = [[f"R{i + 1}", ] for i in range(9)]
    for r in range(9):
        for l in range((r // 3) * 3, (r // 3) * 3 + 3):
            for c in range((r % 3) * 3, (r % 3) * 3 + 3):
                regions[r].append(sudoku[l][c])
    return regions[:]

def get_blocks(sudoku):
    return [*get_rows(sudoku), *get_columns(sudoku), *get_regions(sudoku)]

def get_errors(blocks):
    errors = []
    for block in blocks:
        if set(block[1:]) != {1,2,3,4,5,6,7,8,9}:
            errors.append(block[0])
    return errors[:]

def divide_jobs(jobs, number):
    division = []
    number_jobs = len(jobs)
    q = number_jobs // number
    r = number_jobs % number
    start = 0
    for _ in range(number):
        k = q
        if r:
            r -= 1
            k += 1
        division.append(jobs[start:start+k])
        start += k
    return division[:]

def print_concurrent_errors(errors, process_name):
    dict_size = sum([len(error) for error in errors])
    msg_error = f"{process_name}: {dict_size} erros encontrados "
    if dict_size:
        aux = []
        for i, error in enumerate(errors):
            if len(error):
                aux.append(f"T{i + 1}: " + ", ".join(error))
        msg_error += "(" + "; ".join(aux) + ")"
    print(msg_error)

def print_serial_errors(errors):
    amount_errors = len(errors)
    msg_error = f"Processo main: {amount_errors} erros encontrados "
    if amount_errors:
        msg_error += "(" + ", ".join(errors) + ")"
    print(msg_error)
