# Welcome to the Smart Card Laboratory!

## Resources for the Lab
* For all documentation, such as the lab script, datasheets, reference manuals, reference implementations, please
  visit the course's moodle page.
* A template for your lab protocol can be found here: [here](./templates/benchmarks_template.md)
* A template for the benchmark results can be found here: [here](./templates/lab_report_template.md)

## Useful (external) resources

 * Smart Card Handbook (online) - can be found [here](https://opac.ub.tum.de/search?bvnr=BV019271999)
 * Power analysis attacks - revealing the secrets of smart cards - can be found [here](https://opac.ub.tum.de/search?bvnr=BV036480550)
 * Understanding cryptography -a textbook for students and practitioners- can be found [here](https://opac.ub.tum.de/search?bvnr=BV039865382)


## Initializing submodules in this Repository

In order to compile the demo smartcard os in `demo_os_stm32f051`, you need the Open source ARM
Cortex-M microcontroller library `libopencm3` (https://github.com/libopencm3/libopencm3).
It is already included as a submodule in the git repository. In order to use it, please execute the
following steps.

### Initialize the submodule

As first step, in your shell execute the following command in the directory of this Readme.

```
$ git submodule init
```
### Update the submodule

As soon as the submodule is initialized, download it.

```
$ git submodule update
```

### Build the libopencm3 lib

Build the necessary libopencm3 libraries for the stm32f0 to be linked to your binaries.

```
$ cd demo_os_stm32f051/libopencm3
$ make TARGETS=stm32/f0
```

### Build the test program

Lastly, you can use the Makefile in `demo_os_stm32f051` to build the demo program.
For flashing use either one of the flash scripts in the `scripts` directory.

**Important Notice:**  
If you are working on the student lab PCs, you should not use the system's openocd version,
but the one provided by the SEC nas. In order to enable this config, execute the following
on every fresh terminal you want to use openOCD on.

```
module use /nas/ei/share/sec/tools/modulefiles
module load openocd/latest
```

