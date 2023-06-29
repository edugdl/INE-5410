import sys
import time
import argparse
import matplotlib.pyplot

from concurrent import concurrent_solution
from sequential import sequential_solution
from utils import *


def get_sample(n_process, file, max_threads):
    x = []
    y = []    
    for n_thread in range(1, max_threads + 1):
        start = time.time()
        sys.argv = ["python", file, str(n_process), str(n_thread), "False"]
        concurrent_solution()
        end = time.time()
        x.append(n_thread)
        y.append(end - start)
    
    return x[:], y[:]

def graph():
    parser = argparse.ArgumentParser(add_help=True, description='Gráfico do speedup')

    parser.add_argument('-f', '--file-name', action='store', type=valid_file, required=True, help='O nome do arquivo com as solucoes a serem validadas')
    parser.add_argument('-p', '--max-process', action='store', type=pos_int, required=True, help='O numero máximo de processos trabalhadores')
    parser.add_argument('-t', '--max-threads', action='store', type=pos_int, required=True, help='O numero máximo de threads de correcao a serem utilizadas por cada processo trabalhador')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(1)

    start = time.time()
    sys.argv = ["python", args.file_name, "False"]
    sequential_solution()
    end = time.time()
    sequential_time = end - start

    sudokus = len(read_sudokus(args.file_name))

    print(f"Número de sudokus {sudokus}")
    print("Tempo de referência T(1): ", sequential_time)

    matplotlib.pyplot.title(f'Gráfico speedup (número de sudokus {sudokus})')
    matplotlib.pyplot.xlabel('n_threads')
    matplotlib.pyplot.ylabel('speedup')
    for n_process in range(1, args.max_process + 1):
        x, y = get_sample(n_process, args.file_name, args.max_threads)
        for n_thread, t in zip(x, y):
            print(f"Tempo T({n_process}, {n_thread}): ", t)
        y = [sequential_time / t for t in y]
        matplotlib.pyplot.plot(x, y, label=f'Processos: {n_process}')
        
    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()

if __name__ == "__main__":
    graph()