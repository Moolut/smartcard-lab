#!/bin/sh

# Find path where this script resides
cd "$(dirname $0)"

DBG_BINARY="arm-none-eabi-gdb"
if [ -z "$(which $DBG_BINARY)" ]; then
    DBG_BINARY="gdb-multiarch"
fi

make -C ..

if [ $? == 0 ]; then
    $DBG_BINARY ../demo_os_smartcard.elf -x gdb_conn_openocd -x gdb_commands_flash
fi

