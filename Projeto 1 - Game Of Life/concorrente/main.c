#include <stdio.h>
#include "gol.h"
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    int size, steps;
    cell_t **prev, **next;
    FILE *f;
    stats_t stats_total = {0, 0, 0, 0};

    if (argc != 2)
    {
        printf("ERRO! Você deve digitar %s <nome do arquivo do tabuleiro>!\n\n", argv[0]);
        return 0;
    }

    if ((f = fopen(argv[1], "r")) == NULL)
    {
        printf("ERRO! O arquivo de tabuleiro '%s' não existe!\n\n", argv[1]);
        return 0;
    }

    fscanf(f, "%d %d", &size, &steps);

    prev = allocate_board(size);
    next = allocate_board(size);

    read_file(f, prev, size);

    fclose(f);

#ifdef DEBUG
    printf("Initial:\n");
    print_board(prev, size);
    print_stats(stats_step);
#endif

    int n_threads = sysconf(_SC_NPROCESSORS_ONLN);
    pthread_t threads[n_threads];
    trecho_t trechos[n_threads];
    int q = (size*size) / n_threads;
    int r = (size*size) % n_threads;
    int inicio;
    int fim = 0;

    for (int i = 0; i < n_threads; i++)
    {
        inicio = fim;
        fim += q;
        if (r) {
            fim++;
            r--;
        }
        trechos[i].current_board = prev;
        trechos[i].next_board = next;
        trechos[i].inicial = inicio;
        trechos[i].final = fim;
        trechos[i].size = size;
        trechos[i].steps = steps;
        trechos[i].threads = n_threads;
    }
    
    stats_total = play(size, n_threads, threads, trechos, steps);
    
    prev = trechos[0].current_board;
    next = trechos[0].next_board;
#ifdef RESULT
    printf("Final:\n");
    print_board(prev, size);
    print_stats(stats_total);
#endif

    free_board(prev, size);
    free_board(next, size);
}