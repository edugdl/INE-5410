import os
import argparse

from distutils.util import strtobool

# Função para verificar se o número de threads
# ou processos não é menor que 1
def pos_int(value):
    pos_i = int(value)
    if pos_i < 1:
        msg = "Valor recebido %s. Tente um valor > 0!" % value
        raise argparse.ArgumentTypeError(msg)
    return pos_i

# Função para verificar se o arquivo recebido
# como paramêtro é válido
def valid_file(file):
    if not os.path.exists(file):
        msg = "Valor recebido %s. Arquivo nao existe!" % file
        raise argparse.ArgumentTypeError(msg)
    return file

# Função para verificar se o paramêtro
# enable_output é um booleano
def valid_bool(b):
    return bool(strtobool(b))

# Função ler os sudokus recebidos no arquivo como paramêtro de entrada
def read_sudokus(file):
    sudokus = []
    with open(file) as file:
        # Ele splita duas quebra de linhas para pegar os sudokus
        # e splita uma quebra de linha para pegar as linhas dos sudokus
        sudokus = [[[int(e) for e in line] for line in sudoku.split("\n")] for sudoku in file.read().split("\n\n")]
    return sudokus

# Função para obter todas as linhas
def get_rows(sudoku):
    # L(i+1) é o primeiro elemento da lista e ele indica que é uma linha e 
    # qual será seu respectivo bloco e número, usamos principalmente
    # para o print dos erros
    return [[f"L{i + 1}", *line] for i, line in enumerate(sudoku)]

# Função para obter todas as colunas
def get_columns(sudoku):
    # C(i+1) é o primeiro elemento da lista e ele indica que é uma coluna e 
    # qual será seu respectivo bloco e número, usamos principalmente
    # para o print dos erros
    t = [[sudoku[l][c] for l in range(9)] for c in range(9)]
    return [[f"C{i + 1}", *col] for i, col in enumerate(t)]

def get_regions(sudoku):
    # R(i+1) é o primeiro elemento da lista e ele indica que é uma região e 
    # qual será seu respectivo bloco e número, usamos principalmente
    # para o print dos erros
    regions = [[f"R{i + 1}", ] for i in range(9)]
    for r in range(9):
        for l in range((r // 3) * 3, (r // 3) * 3 + 3):
            for c in range((r % 3) * 3, (r % 3) * 3 + 3):
                regions[r].append(sudoku[l][c])
    return regions[:]

# Obtem todos os blocos em uma unica lista
def get_blocks(sudoku):
    return [*get_rows(sudoku), *get_columns(sudoku), *get_regions(sudoku)]

# Função para obter os erros dos blocos passados por parâmetro
def get_errors(blocks):
    errors = []
    for block in blocks:
        if set(block[1:]) != {1,2,3,4,5,6,7,8,9}:
            errors.append(block[0])
    return errors[:]

# Função para dividir o trabalho(uma divisão de lista) para as threads
# Mesmo método empregado no trabalho anterior
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

# Função para printar os erros na aplicação concorrente
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

# Função para printar os erros na aplicação sequencial
def print_serial_errors(errors):
    amount_errors = len(errors)
    msg_error = f"Processo main: {amount_errors} erros encontrados "
    if amount_errors:
        msg_error += "(" + ", ".join(errors) + ")"
    print(msg_error)
