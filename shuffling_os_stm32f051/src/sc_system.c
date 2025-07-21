#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#include <libopencm3/stm32/flash.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>

#include "sc_system.h"

void sys_gpio_init()
{
    // Enable the GPIO periphal clocks
    rcc_periph_clock_enable(RCC_GPIOA);
    rcc_periph_clock_enable(RCC_GPIOB);

    // Configure the LEDs
    // Set the GPIOs (LEDs are inverted)
    // Red and green led share a GPIO port
    gpio_set(PORT_LED_R, PIN_LED_R | PIN_LED_G);
    // Blue has its own GPIO port
    gpio_set(PORT_LED_B, PIN_LED_B);
    gpio_mode_setup(PORT_LED_R, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, PIN_LED_R | PIN_LED_G);
    gpio_set_output_options(PORT_LED_R, GPIO_OTYPE_OD, GPIO_OSPEED_2MHZ, PIN_LED_R | PIN_LED_G);
    gpio_mode_setup(PORT_LED_B, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, PIN_LED_B);
    gpio_set_output_options(PORT_LED_B, GPIO_OTYPE_OD, GPIO_OSPEED_2MHZ, PIN_LED_B);

    // 7816 Reset Disable Pin
    // By default this pin is strapped low on the pcb. Thus, if a card reader wants to
    // perform a reset, the STM32 will reset, too. In case you are debugging, you might not
    // want your card to be reset everytime the reader sees a timeout.
    gpio_clear(PORT_ISO7816_RST_DIS, PIN_ISO7816_RST_DIS);
    gpio_mode_setup(PORT_ISO7816_RST_DIS, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, PIN_ISO7816_RST_DIS);
    gpio_set_output_options(PORT_ISO7816_RST_DIS, GPIO_OTYPE_PP, GPIO_OSPEED_2MHZ, PIN_ISO7816_RST_DIS);

    // Clock Source Select Pin CLKSEL
    // When low, the STM32 receives the card reader clock on its HSE pin
    // This means, when selecting HSE as clock source, the controller runs with the wonky reader clock
    // this may be favorable for transmitting the ATR and further communication, but unfavorable for
    // performing measurements. Thus, this signal is high by default.
    gpio_set(PORT_CLKSEL, PIN_CLKSEL);
    gpio_mode_setup(PORT_CLKSEL, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, PIN_CLKSEL);
    gpio_set_output_options(PORT_CLKSEL, GPIO_OTYPE_PP, GPIO_OSPEED_2MHZ, PIN_CLKSEL);

    // Trigger Pin
    gpio_clear(PORT_TRIGGER, PIN_TRIGGER);
    gpio_mode_setup(PORT_TRIGGER, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, PIN_TRIGGER);
    gpio_set_output_options(PORT_TRIGGER, GPIO_OTYPE_PP, GPIO_OSPEED_100MHZ, PIN_TRIGGER);
}

void sys_set_reset_source(uint8_t src)
{
    if (src != SYSTEM_RSTSRC_ISO7816 && src != SYSTEM_RSTSRC_DBG_ONLY)
    {
        // Invalid source has been selected -> exit
        return;
    }

    if (src == SYSTEM_RSTSRC_ISO7816)
        gpio_clear(PORT_ISO7816_RST_DIS, PIN_ISO7816_RST_DIS);
    else
        gpio_set(PORT_ISO7816_RST_DIS, PIN_ISO7816_RST_DIS);

    return;
}

void sys_rcc_init()
{
    // Some general settings for the clock configuration

    // Also the card will never have clock speeds > 8 MHz, so keep the
    // flash wait states at zero
    flash_set_ws(FLASH_ACR_LATENCY_0WS);

    // At this time we are running from the HSI, so 8 MHz
    rcc_ahb_frequency = 8000000;
    rcc_apb1_frequency = 8000000;
    rcc_apb2_frequency = 8000000;
}

// Set the desired clock source for the system.
// Changing the system clock requires adjusting divider
// settings throughout the system for peripherals like USART
void sys_set_clksource(uint8_t src)
{
    if (src != SYSTEM_CLKSOURCE_CARD_TERMINAL && src != SYSTEM_CLKSOURCE_EXT_8MHZ)
    {
        // Invalid source has been selected -> exit
        return;
    }

    // As both clock options are being received through the HSE pin,
    // hop on the internal oscillator for the time between changing
    rcc_osc_on(RCC_HSI);
    rcc_wait_for_osc_ready(RCC_HSI);
    rcc_set_sysclk_source(RCC_HSI);

    rcc_osc_off(RCC_HSE);
    // Bypass the oscillator -> we are supplied by a stable clock
    RCC_CR |= RCC_CR_HSEBYP;

    // The desired clock source is the card terminal
    if (src == SYSTEM_CLKSOURCE_CARD_TERMINAL)
    {
        // Set CLKSEL pin low to disable the pcb oscillator
        // and pass through the card terminal clock
        gpio_clear(PORT_CLKSEL, PIN_CLKSEL);
    }
    else
    {
        gpio_set(PORT_CLKSEL, PIN_CLKSEL);
    }

    // Re-enable the HSE
    rcc_osc_on(RCC_HSE);
    rcc_wait_for_osc_ready(RCC_HSE);
    rcc_set_sysclk_source(RCC_HSE);

    // Turn off the HSI
    rcc_osc_off(RCC_HSI);

    return;
}

void delay_cyc(uint32_t cycles)
{
    // The loop translates to roughly two cycles,
    // so just div cycles by two and we good
    cycles = cycles >> 1;
    while (cycles > 0)
    {
        cycles--;
        __asm__("nop");
    }
}
