import sys

from multiprocessing import Process, current_process
from threading import Thread, current_thread, Lock
from utils import *

dones = 0
start = 0

def work_process(sudokus, n_threads, shift, enable_output):
    # Criando uma lista que vai ter os blocos por sudoku por cada thread
    blocks_per_sudokus_per_thread = [[[] for __ in range(n_threads)] for _ in sudokus]
    for i, sudoku in enumerate(sudokus):
        for k, job in enumerate(divide_jobs(get_blocks(sudoku), n_threads)):
            blocks_per_sudokus_per_thread[i][k] = job

    # Inicializando as varíaveis importantes, como os locks e lista de erros e de threads
    threads = []
    locks = [Lock() for _ in range(n_threads)]
    lock_dones = Lock()
    lock_start = Lock()
    errors = [[] for _ in range(n_threads)]
    for k in range(n_threads):
        threads.append(Thread(name=f"T{k + 1}", target=work_threads, args=([blocks_per_sudokus_per_thread[i][k] for i in range(len(sudokus))], shift, enable_output, locks, lock_dones, lock_start, errors)))
        threads[-1].start()

    # Esperando as threads terminarem
    for i, thread in enumerate(threads):
        thread.join()

def work_threads(blocks_per_sudoku, shift, enable_output, locks, lock_done, lock_start, errors):
    # Variaveis necessarias no processamento e output
    global start, dones
    for i, blocks in enumerate(blocks_per_sudoku):
        # Iniciando um lock para cada thread
        locks[int(current_thread().name[1:]) - 1].acquire()
        if enable_output:
            with lock_start:
                # Start serve para garantir que apenas a primeira thread faça esse print
                if start == 0:
                    print(f"{current_process().name}: resolvendo quebra-cabeças {i + shift + 1}")
                start += 1

        # Ordenando a lista de erros para o output ficar na ordem correta
        # Exemplo: {R4,L3,C2,L1}.replace("L", "A") => {R4, A3, C2, A1}.sort() => {A1,A3,C2,R4}.replace("A", "L") => {L1,L3,C2,R4}
        errors[int(current_thread().name[1:]) - 1] = [e.replace("A", "L") for e in sorted([e.replace("L", "A") for e in get_errors(blocks)])]


        with lock_done:
            # Todas a threads irão incrementar essa varíavel
            dones += 1
            # Se a ultima thread terminou reseta as varíavels, limpa os erros e desbloqueia as threads para a próxima iteração(próximo sudoku)
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

def concurrent_solution():
    # Definindo os parametros do programa
    # Fazendo as verificações para cada paramêtro e
    # em caso de um paramêtro do tipo inesperado uma 
    # execeção é disparada e o programa é finalizado
    try:
        if len(sys.argv) not in [4,5]:
            raise IndexError("Passou uma quantidade de argumentos diferente do esperado!")
        file_name = valid_file(sys.argv[1])
        num_process = pos_int(sys.argv[2])
        num_threads = pos_int(sys.argv[3])
        enable_output = True if len(sys.argv) == 4 else valid_bool(sys.argv[4])
    except IndexError as e:
        print(e)
        sys.exit()
    
    # Lendo os sudokus do arquivo passado por paramêtro de programa
    sudokus = read_sudokus(file_name)

    # Se o numero de processos for maior que o numero de sudokus
    # então ele iguala o numero de processos ao numero de sudokus
    if num_process > len(sudokus):
        num_process = len(sudokus)

    # Fazendo a divisao de trabalho das threads e criando-as
    process = []
    jobs = divide_jobs(sudokus, num_process)
    for i in range(num_process):
        process.append(Process(name=f"Processo {i + 1}", target=work_process, args=(jobs[i], num_threads, sum([len(job) for job in jobs[:i]]), enable_output,)))
        process[-1].start()

    # Esperando todos os processos terminarem
    for p in process:
        p.join()

if __name__ == "__main__":
    concurrent_solution()