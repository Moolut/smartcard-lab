#ifndef _AES_H_
#define _AES_H_

#include <stdint.h>
#include <stddef.h>

#define AES_keyExpSize 176

struct AES_ctx
{
    uint8_t RoundKey[AES_keyExpSize];
};

void AES_init_ctx(struct AES_ctx *ctx, const uint8_t *key);


void AES_ECB_decrypt(const struct AES_ctx *ctx, uint8_t *buf, uint8_t *perm);

#endif // _AES_H_