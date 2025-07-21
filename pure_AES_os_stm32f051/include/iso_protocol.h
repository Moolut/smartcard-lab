#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#include <stddef.h>
#include "aes.h"


#endif
#define SIZE(a) sizeof(a) / sizeof(a[0])

static const uint8_t ATR_COMMAND[] = {0x3B, 0x90, 0x11, 0x00}; // ATR bytes as per Python script
static const uint8_t T_0_KEY_COMMAND[] = {0x88, 0x10, 0x00, 0x00, 0x10};
static const uint8_t T_0_KEY_COMMAND_ACK[] = {0x10};
static const uint8_t T_0_KEY_COMMAND_RESP[] = {0x61, 0x10};
static const uint8_t T_0_SEND_KEY_COMMAND[] = {0x88, 0xC0, 0x00, 0x00, 0x10};
static const uint8_t T_0_SEND_KEY_COMMAND_ACK[] = {0xC0};
static const uint8_t T_0_SEND_KEY_COMMAND_RESP[] = {0x90, 0x00};
static const uint8_t T_0_END_RESP[] = {0x90, 0x00};

void start_iso7816(struct AES_ctx *aes_ctx);
void send_atr_command(void);
void receive_key_command(uint8_t *auth_chall);
void send_key_command(uint8_t *auth_resp);
void receive_compare_iso_command(const uint8_t *data, const uint8_t len);
