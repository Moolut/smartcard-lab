#ifndef __ADC_H__
#define __ADC_H__

#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/adc.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/gpio.h>

#define CHANNEL_ARRAY {1, 1, ADC_CHANNEL_TEMP}
#define CHANNEL_ARRAY2 {ADC_CHANNEL_TEMP, ADC_CHANNEL_VREF}

void adc_setup(void);

uint32_t adc_read(void);
#endif