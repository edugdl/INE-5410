import argparse

from multiprocessing import Process, current_process
from threading import Thread, current_thread, Lock
from utils import *

dones = 0
start = 0

def work_process(sudokus, n_threads, shift, enable_output):
    threads = []
    blocks_per_sudokus = [[] for _ in sudokus]
    blocks_per_sudokus_per_thread = [[[] for __ in range(n_threads)] for _ in sudokus]

    for i, sudoku in enumerate(sudokus):
        blocks_per_sudokus[i] = get_blocks(sudoku)

        jobs = divide_jobs(blocks_per_sudokus[i], n_threads)
        for k in range(n_threads):
            blocks_per_sudokus_per_thread[i][k] = jobs[k]

    locks = [Lock() for _ in range(n_threads)]
    lock_dones = Lock()
    lock_start = Lock()
    errors = [[] for _ in range(n_threads)]
    for k in range(n_threads):
        thread = Thread(name=f"T{k + 1}", target=work_threads, args=([blocks_per_sudokus_per_thread[i][k] for i in range(len(sudokus))], shift, enable_output, locks, lock_dones, lock_start, errors))
        thread.start()
        threads.append(thread)

    for i, thread in enumerate(threads):
        thread.join()

def work_threads(blocks_per_sudoku, shift, enable_output, locks, lock_done, lock_start, errors):
    global start
    global dones
    for i, blocks in enumerate(blocks_per_sudoku):

        locks[int(current_thread().name[1:]) - 1].acquire()
        if enable_output:
            with lock_start:
                if start == 0:
                    print(f"{current_process().name}: resolvendo quebra-cabeças {i + shift + 1}")
                start += 1
    
        errors[int(current_thread().name[1:]) - 1] = [e.replace("A", "L") for e in sorted([e.replace("L", "A") for e in get_errors(blocks)])]

        with lock_done:
            dones += 1
            if dones == len(locks):
                dones = 0
                with lock_start:
                    start = 0
                if enable_output:
                    print_concurrent_errors(errors, current_process().name)
                for error in errors:
                    error.clear()
                for lock in locks:
                    lock.release()

def concurrent_solution_v2():
    # Definindo os parametros do programa
    parser = argparse.ArgumentParser(add_help=True, description='Verificador de Sudoku Concorrente em Python')

    parser.add_argument('-f', '--file-name', action='store', type=valid_file, required=True, help='O nome do arquivo com as solucoes a serem validadas')
    parser.add_argument('-p', '--num-process', action='store', type=pos_int, required=True, help='O numero de processos trabalhadores')
    parser.add_argument('-t', '--num-threads', action='store', type=pos_int, required=True, help='O numero de threads de correcao a serem utilizadas por cada processo trabalhador')
    parser.add_argument('-e', '--enable-output', action="store", type=valid_bool, required=False, default=True,  help='Ativa oudesativa so prints')
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
    concurrent_solution_v2()