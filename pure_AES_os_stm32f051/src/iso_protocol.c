#include <stddef.h>

#include "sc_system.h"
#include "iso_protocol.h"
#include "aes.h"

void send_atr_command(void)
{
    // Send the ATR
    usart_send_bytes(ATR_COMMAND, SIZE(ATR_COMMAND));
}

void start_iso7816(struct AES_ctx *aes_ctx)
{
    uint8_t key[16];
    // Receive Decrypt Key Command (0x88 0x10 0x00 0x00 0x10)
    // and decrypt the key data
    receive_key_command(key);

    // AES decrypt start
    uint8_t *dec_key = key;
    gpio_set(PORT_TRIGGER, PIN_TRIGGER);
    AES_ECB_decrypt(aes_ctx, dec_key);
    gpio_clear(PORT_TRIGGER, PIN_TRIGGER);
    // AES decrypt end

    // Send the Decrypt Key Command Response
    // (0x61 0x10)
    usart_send_bytes(T_0_KEY_COMMAND_RESP, SIZE(T_0_KEY_COMMAND_RESP));

    // Receive get response command (0x88 0xC0 0x00 0x00 0x10)
    // send the decrypted key data
    // send the final response (0x90 0x00)
    send_key_command(dec_key);
}

void receive_key_command(uint8_t *key)
{
    receive_compare_iso_command(T_0_KEY_COMMAND, SIZE(T_0_KEY_COMMAND));

    // Send ACK by the size of the message
    usart_send_bytes(T_0_KEY_COMMAND_ACK, SIZE(T_0_KEY_COMMAND_ACK));

    for (int i = 0; i < 16; i++)
    {
        key[i] = usart_receive_byte();
    }
}

void send_key_command(uint8_t *dec_key)
{
    // Receive the send key command
    receive_compare_iso_command(T_0_SEND_KEY_COMMAND, SIZE(T_0_SEND_KEY_COMMAND));

    // Send ACK => 0xC0
    usart_send_bytes(T_0_SEND_KEY_COMMAND_ACK, SIZE(T_0_SEND_KEY_COMMAND_ACK));

    // Send the decrypted key
    usart_send_bytes(dec_key, 16);

    // Send the final response
    usart_send_bytes(T_0_END_RESP, SIZE(T_0_END_RESP));
}

void receive_compare_iso_command(const uint8_t *data, const uint8_t len)
{

    for (int i = 0; i < len; i++)
    {
        uint8_t byte_expected = data[i];
        uint8_t byte_received = usart_receive_byte();

        if (byte_expected != byte_received)
        {
            gpio_toggle(PORT_LED_R, PIN_LED_R);
            delay_cyc(500000000);
            gpio_toggle(PORT_LED_R, PIN_LED_R);
            delay_cyc(500000000);
        }
    }
}
