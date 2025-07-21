#ifndef _SHUFFLE_H_
#define _SHUFFLE_H_

#include <stdint.h>
#include <stddef.h>
#include "entropy.h"

void generate_permutation(uint8_t *perm, uint8_t len, EntropyPool *ep);

#endif