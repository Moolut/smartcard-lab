
#include <libopencm3/cm3/nvic.h>
#include "entropy.h"
#include "usart.h"

static inline int is_full(EntropyPool *ep)
{
    if (ep->head == 0 && ep->tail == ep->num_chunks - 1)
        return 1;
    else if (ep->tail == ep->head - 1)
        return 1;
    else
    {
    }

    return 0;
}

static inline int is_empty(EntropyPool *ep)
{
    return (ep->count < 32);
}

static inline void inc_tail(EntropyPool *ep)
{
    if (ep->tail == ep->num_chunks - 1)
        ep->tail = 0;
    else
        ep->tail++;
}

static inline void inc_head(EntropyPool *ep)
{
    if (ep->head == ep->num_chunks - 1)
        ep->head = 0;
    else
        ep->head++;
}

void entropy_init(EntropyPool *ep)
{
    ep->num_chunks = POOL_SIZE * 32; // Total number of bits in the pool
    ep->head = 0;                    // Start of the pool
    ep->tail = 0;                    // End of the pool
    ep->count = 0;                   // Current number of bits in the pool
}


void entropy_append_to_pool(EntropyPool *ep, uint32_t val)
{
    if (is_full(ep))
    {
        return; // Pool is full; do nothing
    }

    uint32_t bit_pos = ep->tail % 32;
    uint32_t word_ind = ep->tail / 32;
    uint32_t mask = ~(1 << bit_pos);

    ep->pool[word_ind] &= mask;
    ep->pool[word_ind] |= (val & 0x1) << bit_pos;

    inc_tail(ep);
    ep->count++;

    // usart2_puts("Entropy appended. Current count: ");
    // usart2_puti(ep->count);
    // usart2_puts("\n");
}

uint32_t entropy_get_random(EntropyPool *ep, uint32_t *val)
{
    uint32_t ret = 0;

    if (is_empty(ep))
    {
        return 1; // Pool empty
    }

    *val = 0;
    for (uint8_t i = 0; i < 32; i++)
    {
        uint32_t bit_pos = ep->head % 32;
        uint32_t word_ind = ep->head / 32;

        *val |= ((ep->pool[word_ind] >> bit_pos) & 0x1) << i;

        inc_head(ep);
    }

    ep->count -= 32;
    return ret;
}
