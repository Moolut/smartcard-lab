##
## This file is part of the libopencm3 project.
##
## Copyright (C) 2009 Uwe Hermann <uwe@hermann-uwe.de>
##
## This library is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this library.  If not, see <http://www.gnu.org/licenses/>.
##
OPENCM3_DIR = ./libopencm3

BUILD_DIR    = build
PROJECT      = demo_os_smartcard
SMARTCARD_HW = SMARTCARD_HW_V3

CFILES     = src/main.c src/sc_system.c src/aes.c src/usart.c src/iso_protocol.c src/adc.c src/prng.c src/shuffle.c
SHARED_DIR = include/
VPATH     += $(SHARED_DIR)
INCLUDES  += $(patsubst %, -I%, . $(SHARED_DIR))
OPT        = -Og
CSTD       = -std=c99

DEVICE       = stm32f051k8b6
# LDSCRIPT   = stm32f051k8b6 use device OR ldscript
OPENCM3_LIB  = opencm3_stm32f0
OPENCM3_DEFS = -DSTM32F0 -D$(SMARTCARD_HW)
ARCH_FLAGS   =
FP_FLAGS     = -msoft-float
ARCH_FLAGS   = -mthumb -mcpu=cortex-m3 $(FP_FLAGS)

include $(OPENCM3_DIR)/mk/genlink-config.mk
include rules.mk
include $(OPENCM3_DIR)/mk/genlink-rules.mk


