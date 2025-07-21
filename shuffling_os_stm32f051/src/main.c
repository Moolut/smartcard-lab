#include <string.h>
#include <libopencm3/stm32/gpio.h>

#include "sc_system.h"
#include "usart.h"
#include "iso_protocol.h"
#include "entropy.h"
#include "shuffle.h"
#include "global.h"
#include "adc.h"
#include "prng.h"

uint8_t MASTER_KEY[16] = {0xA2, 0xD0, 0xF1, 0x24, 0x4A, 0xAA, 0x94, 0xD0, 0xA7, 0x25, 0x4F, 0x26, 0xEB, 0x6D, 0x88, 0x05};
struct AES_ctx aes_ctx;
EntropyPool ep;

int main(void)
{
    // Define state variable

    sys_rcc_init();
    // Init the GPIOs so we can config
    // the clock source and ISO7816 reset behavior
    sys_gpio_init();
    sys_set_clksource(SYSTEM_CLKSOURCE_EXT_8MHZ);
    sys_set_reset_source(SYSTEM_RSTSRC_DBG_ONLY);

    usart_init();

    // entropy_init(&ep);
    adc_setup();

    // Read the ADC values to seed the entropy pool
    uint32_t prng_seed = adc_read();

    PRNG_Init(&ep, prng_seed);

    send_atr_command();
    AES_init_ctx(&aes_ctx, MASTER_KEY);

    while (1)
    {

        uint32_t rand = adc_read();

        // usart2_puti(rand);

        uint8_t perm[16];
        generate_permutation(perm, 16, NULL); // Generate a random permutation of 16 bytes

        start_iso7816(&aes_ctx, perm);
        PRNG_Reseed(&ep, rand);
    }

    return 0;
}
