#ifndef __USART_H__
#define __USART_H__

#include <stddef.h>

#include <libopencm3/stm32/gpio.h>

#endif

#define F_CLOCK_RATE_CONVERSION_INT 372
#define D_BAUD_RATE_ADJ_INT 1
#define OS_CLOCK 4750000

void usart_init();
void usart_set_mode_transmit(void);
void usart_set_mode_receive(void);
void usart_send_byte(uint8_t data);
void usart_send_bytes(uint8_t *data, size_t len);
uint8_t usart_receive_byte(void);
