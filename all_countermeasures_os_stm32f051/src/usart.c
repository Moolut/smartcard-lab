#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>

#include "sc_system.h"
#include "usart.h"

void usart_init()
{
    // Enable the USART1 peripheral clock   
    rcc_periph_clock_enable(RCC_USART1);
    rcc_periph_clock_enable(RCC_USART2);

    // Configure GPIOs for USART1 TX
    gpio_mode_setup(PORT_USART1_TX, GPIO_MODE_AF, GPIO_PUPD_NONE, PIN_USART1_TX);
    gpio_set_output_options(PORT_USART1_TX, GPIO_OTYPE_PP, GPIO_OSPEED_2MHZ, PIN_USART1_TX);
    gpio_set_af(PORT_USART1_TX, GPIO_AF1, PIN_USART1_TX);

    usart_set_baudrate(USART1, (OS_CLOCK / (F_CLOCK_RATE_CONVERSION_INT * D_BAUD_RATE_ADJ_INT)));

    // Configure USART1 Smartcard mode
    USART1_CR3 |= USART_CR3_SCEN;                           // Enable Smartcard mode
    USART1_CR2 |= USART_CR2_STOPBITS_1_5 | USART_CR2_CLKEN; // 1.5 stop bits, enable clock
    USART1_CR1 |= USART_CR1_M |                             // Enable 9-bit data mode (8-data bits + parity)
                  USART_CR1_PCE |                           // Enable parity control
                  USART_CR1_UE;                             // Enable USART


    // --- USART2 Configuration (Standard Async Mode) ---

    gpio_mode_setup(PORT_USART2_TX, GPIO_MODE_AF, GPIO_PUPD_NONE, PIN_USART2_TX);
    gpio_set_output_options(PORT_USART2_TX, GPIO_OTYPE_PP, GPIO_OSPEED_2MHZ, PIN_USART2_TX);
    gpio_set_af(PORT_USART2_TX, GPIO_AF1, PIN_USART2_TX);
    
    usart_set_baudrate(USART2, 115200);

    USART2_CR1 = USART_CR1_TE | USART_CR1_UE; // Enable transmitter, receiver and USART

    return;
}

void usart_set_mode_transmit(void)
{

    USART1_CR1 |= USART_CR1_TE;  // Enable transmitter
    USART1_CR1 &= ~USART_CR1_RE; // Disable receiver
}

void usart_set_mode_receive(void)
{

    USART1_CR1 |= USART_CR1_RE;  // Enable receiver
    USART1_CR1 &= ~USART_CR1_TE; // Disable transmitter
}

void usart_send_byte(uint8_t data)
{
    // Send the data
    USART1_TDR = data;
}

void usart_send_bytes(uint8_t *data, size_t len)
{
    usart_set_mode_transmit();

    for (size_t i = 0; i < len; i++)
    {
        // Wait until the transmit buffer is empty
        while (!(USART1_ISR & USART_ISR_TXE))
            ;

        // Send the data
        usart_send_byte(data[i]);
    }

    // Wait for the last byte to complete transmission
    while (!(USART1_ISR & USART_ISR_TC))
        ;

    // Clear the TC flag
    USART1_ICR |= USART_ICR_TCCF;
}

uint8_t usart_receive_byte(void)
{
    usart_set_mode_receive();

    // Wait until the receive buffer is full
    while (!(USART1_ISR & USART_ISR_RXNE))
        ;

    // Read the data
    return (uint8_t)USART1_RDR;
}


void usart2_putc(char c)
{
    USART2_TDR = c;
}

void usart2_puts(const char *s)
{

    while (*s)
    {
        // Wait until the transmit buffer is empty
        while (!(USART2_ISR & USART_ISR_TXE))
            ;

        // Send the data
        usart2_putc(*s++);
    }

    // Wait for the last byte to complete transmission
    while (!(USART2_ISR & USART_ISR_TC))
        ;

    // Clear the TC flag
    USART2_ICR |= USART_ICR_TCCF;

}

void usart2_puti(int number)
{
    char buffer[20]; // Buffer to hold the converted string

    // Convert the integer to a string
    sprintf(buffer, "%d", number);

    // Pass the string to usart2_puts
    usart2_puts(buffer);
}