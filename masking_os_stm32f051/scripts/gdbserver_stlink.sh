#!/bin/sh

openocd -f "interface/stlink.cfg" -f "target/stm32f0x.cfg" -c "adapter speed 100" -c "reset_config srst_only" #connect_assert_srst"

# -c "reset_config srst_only srst_nogate connect_assert_srst"
