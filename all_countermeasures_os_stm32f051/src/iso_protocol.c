#include <stddef.h>

#include "sc_system.h"
#include "iso_protocol.h"
#include "aes.h"
#include "usart.h"
#include "entropy.h"

void send_atr_command(void)
{
    // Send the ATR
    usart_send_bytes(ATR_COMMAND, SIZE(ATR_COMMAND));
}

void start_iso7816(struct AES_ctx *aes_ctx, uint8_t *perm)
{

    uint8_t key[16];

    // Receive the key
    receive_key_command(key);

    uint8_t *dec_key = key;

    // AES start
    gpio_set(PORT_TRIGGER, PIN_TRIGGER);
    AES_ECB_decrypt(aes_ctx, dec_key, perm);
    gpio_clear(PORT_TRIGGER, PIN_TRIGGER);
    // AES end

    // Send the key command response
    usart_send_bytes(T_0_KEY_COMMAND_RESP, SIZE(T_0_KEY_COMMAND_RESP));

    // Send the decrypted key
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
