#!/bin/sh

# Find path where this script resides
cd "$(dirname $0)"

make clean -C ..
make -C ..

if [ $? -eq 0 ]; then
    openocd -f "interface/stlink.cfg" -f "target/stm32f0x.cfg" -c "adapter speed 8000" \
         -c "reset_config srst_only connect_assert_srst" -c "program ../demo_os_smartcard.elf verify reset exit"
fi

