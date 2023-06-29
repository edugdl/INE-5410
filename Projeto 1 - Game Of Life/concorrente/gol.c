/*
 * The Game of Life
 *
 * RULES:
 *  1. A cell is born, if it has exactly three neighbours.
 *  2. A cell dies of loneliness, if it has less than two neighbours.
 *  3. A cell dies of overcrowding, if it has more than three neighbours.
 *  4. A cell survives to the next generation, if it does not die of lonelines or overcrowding.
 *
 * In this version, a 2D array of ints is used.  A 1 cell is on, a 0 cell is off.
 * The game plays a number of steps (given by the input), printing to the screen each time.
 * A 'x' printed means on, space means off.
 *
 */

#include <stdlib.h>
#include "gol.h"
#include <pthread.h>
#include <semaphore.h>

sem_t mutex_done;

int done = 0;

void *funcao(void *arg) {
    trecho_t *t = (trecho_t *)arg;
    for (int i = 0; i < t->steps; i++) {
        sem_wait(&t->mutexes[t->index]);
        for (int k = t->inicial; k < t->final; k++)
        {
            int i = k / t->size;
            int j = k % t->size;

            int a = adjacent_to(t->current_board, t->size, i, j);

            /* if cell is alive */
            if(t->current_board[i][j]) 
            {
                /* death: loneliness */
                if(a < 2) {
                    t->next_board[i][j] = 0;
                    t->stats.loneliness++;
                }
                else
                {
                    /* survival */
                    if(a == 2 || a == 3)
                    {
                        t->next_board[i][j] = t->current_board[i][j];
                        t->stats.survivals++;
                    }
                    else
                    {                   
                        /* death: overcrowding */
                        if(a > 3)
                        {
                            t->next_board[i][j] = 0;
                            t->stats.overcrowding++;
                        }
                    }
                }
                
            }
            else /* if cell is dead */
            {
                if(a == 3) /* new born */
                {
                    t->next_board[i][j] = 1;
                    t->stats.borns++;
                }
                else /* stay unchanged */
                    t->next_board[i][j] = t->current_board[i][j];
            }
        }
        cell_t **aux = t->next_board;
        t->next_board = t->current_board;
        t->current_board = aux;
        sem_wait(&mutex_done);
        done++;
        if (done == t->threads) {
            done = 0;
            for (int i = 0; i < t->threads; i++)
                sem_post(&t->mutexes[i]);
        }
        sem_post(&mutex_done);

    }
    pthread_exit(NULL);
}

/* Statistics */
stats_t statistics;

cell_t **allocate_board(int size)
{
    cell_t **board = (cell_t **)malloc(sizeof(cell_t *) * size);
    int i;
    for (i = 0; i < size; i++)
        board[i] = (cell_t *)malloc(sizeof(cell_t) * size);
    
    statistics.borns = 0;
    statistics.survivals = 0;
    statistics.loneliness = 0;
    statistics.overcrowding = 0;

    return board;
}

void free_board(cell_t **board, int size)
{
    int i;
    for (i = 0; i < size; i++)
        free(board[i]);
    free(board);
}

int adjacent_to(cell_t **board, int size, int i, int j)
{
    int k, l, count = 0;

    int sk = (i > 0) ? i - 1 : i;
    int ek = (i + 1 < size) ? i + 1 : i;
    int sl = (j > 0) ? j - 1 : j;
    int el = (j + 1 < size) ? j + 1 : j;

    for (k = sk; k <= ek; k++)
        for (l = sl; l <= el; l++)
            count += board[k][l];
    count -= board[i][j];

    return count;
}

stats_t play(int size, int n_threads, pthread_t *threads, trecho_t *trechos, int steps)
{   
    stats_t stats = {0,0,0,0};
    sem_t mutexes[n_threads];

    sem_init(&mutex_done, 0, 1);

    for (int i = 0; i < n_threads; i++)
    {
        sem_init(&mutexes[i], 0, 1);
        trechos[i].mutexes = mutexes;
        trechos[i].index = i;
        trechos[i].stats = stats;
        pthread_create(&threads[i],NULL, funcao, (void*)&trechos[i]);
    }
    
    for (int i = 0; i < n_threads; i++)
    {
        pthread_join(threads[i], NULL);
        stats.borns += trechos[i].stats.borns;
        stats.loneliness += trechos[i].stats.loneliness;
        stats.overcrowding += trechos[i].stats.overcrowding;
        stats.survivals += trechos[i].stats.survivals;
        sem_destroy(&mutexes[i]);
    }
    sem_destroy(&mutex_done);

    return stats;
}

void print_board(cell_t **board, int size)
{
    int i, j;
    /* for each row */
    for (j = 0; j < size; j++)
    {
        /* print each column position... */
        for (i = 0; i < size; i++)
            printf("%c", board[i][j] ? 'x' : ' ');
        /* followed by a carriage return */
        printf("\n");
    }
}

void print_stats(stats_t stats)
{
    /* print final statistics */
    printf("Statistics:\n\tBorns..............: %u\n\tSurvivals..........: %u\n\tLoneliness deaths..: %u\n\tOvercrowding deaths: %u\n\n",
        stats.borns, stats.survivals, stats.loneliness, stats.overcrowding);
}

void read_file(FILE *f, cell_t **board, int size)
{
    char *s = (char *) malloc(size + 10);

    /* read the first new line (it will be ignored) */
    fgets(s, size + 10, f);

    /* read the life board */
    for (int j = 0; j < size; j++)
    {
        /* get a string */
        fgets(s, size + 10, f);

        /* copy the string to the life board */
        for (int i = 0; i < size; i++)
            board[i][j] = (s[i] == 'x');
    }

    free(s);
}