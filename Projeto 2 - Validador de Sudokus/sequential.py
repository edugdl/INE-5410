import argparse

from distutils.util import strtobool
from utils import *

def worker(sudokus, enable_output):
    for i, sudoku in enumerate(sudokus):
        blocks = get_blocks(sudoku)
        
        if enable_output:
            print(f"Processo main: resolvendo quebra-cabeças {i}")

        errors = get_errors(blocks)

        if enable_output:
            print_serial_errors(errors[:])

def sequential_solution():
    parser = argparse.ArgumentParser(add_help=True, description='Verificador de Sudoku Concorrente em Python')

    parser.add_argument('-f', '--file-name', action='store', type=valid_file, required=True, help='O nome do arquivo com as solucoes a serem validadas')
    parser.add_argument('-e', '--enable_output', action="store", type=lambda x:bool(strtobool(x)), required=False, default=True,  help='Ativa ou desativa os prints')

    # Tratando eventuais erros de entrada
    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(1)

    sudokus = read_sudokus(args.file_name)
    
    worker(sudokus, args.enable_output)

if __name__ == "__main__":
    sequential_solution()