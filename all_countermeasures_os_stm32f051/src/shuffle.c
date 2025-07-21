#include "shuffle.h"
#include "entropy.h"
#include "prng.h"
#include <stdint.h>

void generate_permutation(uint8_t *perm, uint8_t len, EntropyPool *ep)
{
    for (uint8_t i = 0; i < len; i++)
    {
        perm[i] = i; // Initialize with identity mapping
    }

    // Shuffle the array using Fisher-Yates algorithm
    for (uint8_t i = len - 1; i > 0; i--)
    {
        uint32_t rand = PRNG_Generate();
        // if (entropy_get_random(ep, &rand) != 0)
        // {
        //     // Handle entropy pool empty case
        //     rand = i; // Fallback to deterministic behavior (not secure but avoids crash)
        // }
        uint8_t j = rand % (i + 1);

        // Swap perm[i] and perm[j]
        uint8_t temp = perm[i];
        perm[i] = perm[j];
        perm[j] = temp;
    }
}
