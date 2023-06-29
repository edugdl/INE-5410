import argparse

from multiprocessing import Process, current_process
from threading import Thread
from utils import *


def work_process(sudokus, n_threads, shift, enable_output):
    threads = []

    for i, sudoku in enumerate(sudokus):
        
        if enable_output:
            print(f"{current_process().name}: resolvendo quebra-cabeças {i + shift + 1}")
    
        blocks = get_blocks(sudoku)
        errors = [[] for _ in range(n_threads)]
        jobs = divide_jobs(blocks, n_threads)
        for k in range(n_threads):
            thread = Thread(name=f"T{k + 1}", target=work_threads, args=(jobs[k], errors[k]))
            thread.start()
            threads.append(thread)

        for i, thread in enumerate(threads):
            thread.join()

        if enable_output:
            print_concurrent_errors(errors, current_process().name)

def work_threads(blocks, errors):
    [errors.append(e.replace("A", "L")) for e in sorted([e.replace("L", "A") for e in get_errors(blocks)])]

def concurrent_solution_v1():
    # Definindo os parametros do programa
    parser = argparse.ArgumentParser(add_help=True, description='Verificador de Sudoku Concorrente em Python')

    parser.add_argument('-f', '--file-name', action='store', type=valid_file, required=True, help='O nome do arquivo com as solucoes a serem validadas')
    parser.add_argument('-p', '--num-process', action='store', type=pos_int, required=True, help='O numero de processos trabalhadores')
    parser.add_argument('-t', '--num-threads', action='store', type=pos_int, required=True, help='O numero de threads de correcao a serem utilizadas por cada processo trabalhador')
    parser.add_argument('-e', '--enable-output', action="store", type=valid_bool, required=False, default=True,  help='Ativa ou desativa os prints')
    # Tratando eventuais erros de entrada
    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(1)

    sudokus = read_sudokus(args.file_name)

    if args.num_process > len(sudokus):
        args.num_process = len(sudokus)

    # Fazendo a divisao de trabalho das threads
    process = []
    jobs = divide_jobs(sudokus, args.num_process)
    for i in range(args.num_process):
        p = Process(name=f"Processo {i + 1}", target=work_process, args=(jobs[i], args.num_threads, sum([len(job) for job in jobs[:i]]), args.enable_output,))
        p.start()
        process.append(p)

    for p in process:
        p.join()

if __name__ == "__main__":
    concurrent_solution_v1()