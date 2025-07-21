#ifndef PRNG_H
#define PRNG_H

#include <stdint.h>
#include <stddef.h>
#include "entropy.h" // Include for TRNG functions

// PRNG Initialization
void PRNG_Init(EntropyPool *ep, uint32_t seed);
void PRNG_Reseed(EntropyPool *ep, uint32_t seed);

// Generate a 32-bit random number
uint32_t PRNG_Generate();

// Generate an array of random bytes
void PRNG_GenerateBytes(uint8_t *output, size_t length);

#endif // PRNG_H