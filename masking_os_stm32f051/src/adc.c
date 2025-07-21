
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/adc.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/gpio.h>

#include "adc.h"
#include "global.h"
#include "entropy.h"
#include "sc_system.h"
#include "usart.h"

uint8_t channel_array[] = CHANNEL_ARRAY;
uint8_t channel_array2[] = CHANNEL_ARRAY2;
void adc_setup(void)
{
    rcc_periph_clock_enable(RCC_ADC);
    rcc_periph_clock_enable(RCC_GPIOA);

    // Basic ADC setup
    adc_power_off(ADC1);
    adc_calibrate(ADC1);
    adc_set_clk_source(ADC1, ADC_CLKSOURCE_ADC);

    adc_enable_temperature_sensor();
    adc_set_sample_time_on_all_channels(ADC1, ADC_SMPTIME_013DOT5); // Shortest sampling time for maximum jitter
    adc_set_resolution(ADC1, ADC_RESOLUTION_12BIT);                 // High resolution for more bits
    adc_set_regular_sequence(ADC1, 1, channel_array2);

    adc_power_on(ADC1);
}

uint32_t adc_read(void)
{
    uint32_t rand_value = 0;
    uint8_t bit_position = 0;

    // Collect enough valid bits to form a 32-bit random value
    while (bit_position < 32)
    {
        adc_start_conversion_regular(ADC1);
        while (!(adc_eoc(ADC1)))
            ;                                          // Wait for ADC conversion
        uint32_t adc_value_1 = adc_read_regular(ADC1); // Read first ADC value
        uint32_t lsb_value_1 = adc_value_1 & 0x1;      // Extract LSB

        adc_start_conversion_regular(ADC1);
        while (!(adc_eoc(ADC1)))
            ;                                          // Wait for second ADC conversion
        uint32_t adc_value_2 = adc_read_regular(ADC1); // Read second ADC value
        uint32_t lsb_value_2 = adc_value_2 & 0x1;      // Extract LSB

        // XOR the two LSBs and add to the result
        uint32_t xor_result = lsb_value_1 ^ lsb_value_2;
        rand_value |= (xor_result << bit_position); // Add the result to the random value
        bit_position++;

        // delay_cyc(10); // Allow time for jitter
    }
    return rand_value;
}