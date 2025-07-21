#ifndef _ENTROPY_H_
#define _ENTROPY_H_

#define POOL_SIZE 2

typedef struct
{
    uint32_t pool[POOL_SIZE];
    volatile uint8_t head, tail;
    uint8_t count;
    uint8_t num_chunks;
} EntropyPool;

void entropy_init(EntropyPool *ep);
void entropy_append_to_pool(EntropyPool *ep, uint32_t val);
uint32_t entropy_get_random(EntropyPool *ep, uint32_t *val);

#endif