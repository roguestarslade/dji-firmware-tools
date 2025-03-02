# dji-firmware-tools

Tools for extracting, modding and re-packaging firmwares of [DJI](http://www.dji.com) multirotor drones.

# Motivation

The project started as an alternative implementation of the parser from [phantom-licensecheck](https://github.com/probonopd/phantom-licensecheck).
Over time it has grown to support many generations of DJI products.
It consists of tools which allow not only extraction, but also re-packing of
the previously extracted modules back into single file. There are also tools
which are supposed to be used on specific modules to extract and allow modification
of their content.

# Use cases

Here are a few of possible uses of the tools.

### Calibration after repair

Replacing some components of the drone may require calibration. The tools are
capable of triggering calibration in some devices, mostly gimbals with
[Hall sensors](https://en.wikipedia.org/wiki/Hall_effect_sensor).

It is also possible to use them to send any custom packet to the drone, and
this way trigger factory functions like calibration or pairing - as long
as you know how the packet should look like.

### Parts identification on board and component level

The [wiki of this project](https://github.com/o-gs/dji-firmware-tools/wiki)
has tons of information about boards within each drone,
and components on each board. This info is created and shared by many enthusiasts
and repair technicians.

### Flight parameters modification

The tools can be used as command line version of DJI Assistant software,
which also allows to change parameters for platforms which lacks such
OEM software or where it has the advanced functions locked.

Flight Controllers from DJI define hunderds of parameters which affect their
behavior. These can be modified by just sending a command to the drone,
as long as the new value is within limits accepted by FC firmware.

### Firmware modification

The tools allow modifying firmware binaries, and then re-packing them back
into flashable firmware package. This way, any software-controled functionality
can be altered, including:
* hardware pairing can be disabled,
* allowed value ranges of parameters can be changed,
* all hard-coded limits can be lifted or extended,
* unused hardware features can be enabled,
* additional devices can be added and integrated to the drone,
* anything you can imagine, as long as you're capable of implementing the change.

It may sometimes require additional knowledge and software modifications
(ie. rooting the drone) to flash modified firmware - some firmware packages
are signed using asymmetric cryptography, and private keys are rarely available.

### Research

If you're interested in DJI hardware and software, this is the place to start
learning. You can:

* capture and analyze communication between modules within the drone and RC
to figure out what specific hardware and software does,
* use the wiki to compare hardware and software between platforms, or to analyze
boards on component level before opening your drone,
* extract firmware update packages to analyze and compare binaries executed by
each programmable chip within the drone,
* analyze a specific binary from firmware, for example by converting it to ELF
and using disassembler to look at the content, applying symbols for easier
understanding of what the code does,
* find security vulnerabilities within firmware binaries and communication protocols,
* compare firmware binaries between FW package versions,
* parse flight logs generated by the drones,
* get some basic knowledge to not act stupid when interacting with community
of modders or researchers.

# Step by step instruction

Such instruction will not be provided. These tools are for engineers with vast
hardware and software knowledge. You need to know what you're doing to achieve
anything with these tools.

This is to make sure the tools won't be used by script kiddies to disable
security mechanisms and to allow breaking local laws.

If you can't understand how the tools work, you should not use them. If any
warnings are shown, you must investigate the cause to make sure final firmware
will not be damaged. You are using the tools on your own risk.

# Firmware structure

Since all the tools are available in source code form, it is easy to check details
on the structure and protocols processed by these tools by looking at their source.
The source code is intended to also act as a format documentation.

For higher level and more hardware related info, check [the project Wiki](https://github.com/o-gs/dji-firmware-tools/wiki).

# Tools

The tools can be divided into two categories:

* Hardware-independent tools - Those for which you do not need to have any DJI product
to use. You just need an input file they use, like DJI Firmware Package or DAT Log file.

* Product Communication tools - You need to connect your drone to a PC in order
to use these tools in any meaningful way. Currently the tools use serial interface
(UART) and I2C.

Below the specific tools are described in short. Running them without parameters
will give you details on supported commands in each of them.

To get specifics about command line arguments of each tool, run them with `--help`
option. Some tools also have additional remarks in their headers - try viewing them.

### dji_xv4_fwcon.py

DJI Firmware xV4 Container tool; allows extracting modules from package file which
starts with `xV4`, or creating container by merging firmware modules. Use this tool
first, to extract the BIN file downloaded from DJI, as long as the file starts with
`xV4`.

Example of extracting modules from DJI firmware package for *Phantom 3 Pro*:

```./dji_xv4_fwcon.py -vv -x -p P3X_FW_V01.08.0080.bin```

### dji_imah_fwsig.py

DJI Firmware IMaH Un-signer and Decryptor tool; allows to decrypt and un-sign module
from `.sig` file which starts with `IM*H`. Use this tool after untarring single
modules from a firmware package, to decrypt its content. The tool can also re-sign
a module, as long as private part of the chosen key is available.

Keys used for encryption and authentication were changing over time; when an
`IM*H` file refers to a key for which the tool has several versions, it will
display a list of possible keys in a warning message, and select the most
recent key for current operation.

Example of un-signing Camera firmware for *Mavic Pro*:

```./dji_imah_fwsig.py -vv -k PRAK-2017-01 -k PUEK-2017-07 -u -i wm220_0101_v02.00.55.69_20161215.pro.fw.sig```

Example of un-signing FC firmware for *Phantom 4 Pro V2*:

```./dji_imah_fwsig.py -vv -k PRAK-2017-01 -k PUEK-2017-07 -u -i wm335_0306_v03.03.04.10_20180429.pro.fw.sig```

Example of signing previously un-signed FC firmware for *Mini 2* (requires `PRAK` with private part):

```./dji_imah_fwsig.py -vv -k PRAK-2019-09 -s -i wm161_0306_v03.04.09.74_20210112.pro.fw.sig```

For more examples of usage of the tool, as well as identifiers of keys for specific
platforms, read the script used for testing it: `tests/test_dji_imah_fwsig_rebin1.sh`.

### dji_mvfc_fwpak.py

DJI Mavic Flight Controller Firmware Decryptor tool; removes second layer encryption
in Flight Controller firmware modules from several DJI products released around the
same period: *Mavic Pro*, *Spark*, *Inspire 2* and *Phantom 4*. Does not accept `IM*H`
format - requires input files with first level encryption already removed.

Example of decrypting FC firmware for *Mavic Pro*:

```./dji_mvfc_fwpak.py dec -i wm220_0306_v03.02.40.11_20170918.pro.fw```

### amba_fwpak.py

Ambarella A7/A9 firmware pack tool; allows extracting partitions from the
firmware, or merging them back. Use this to extract Ambarella firmware from
files created after DJI Container is extracted. You can recognize the Ambarella
firmware by a lot of "Amba" strings within, or by a 32-char zero-padded string
at the beginning of the file.

Example of extracting partitions from Ambarella firmware for *Phantom 3 Pro*:

```./amba_fwpak.py -vv -x -m P3X_FW_V01.08.0080_m0100.bin```

### amba_romfs.py

Ambarella A7/A9 firmware ROMFS filesystem tool; allows extracting single files
from ROMFS filesystem file, or rebuilding filesystem from the single files.
Use this after the Ambarella firmware is extracted. You can recognize ROMFS
partitions by file names near beginning of the file, surrounded by blocks of
0xff filled bytes.

Example of extracting ROMFS partition from Ambarella firmware for *Phantom 3 Pro*:

```./amba_romfs.py -vv -x -p P3X_FW_V01.08.0080_m0100_part_rom_fw.a9s```

### amba_ubifs.sh

Linux script for mounting UBIFS partition from the Ambarella firmware. After
mounting, the files can be copied or modified. Use this after the Ambarella
firmware is extracted. The file containing UBIFS can be easily recognized
by `UBI#` at the beginning of the file.

Example of mounting Root Filesystem partition from Ambarella firmware for *Phantom 3 Pro*:

```sudo ./amba_ubifs.sh P3X_FW_V01.08.0080_m0100_part_rfs.a9s```


### arm_bin2elf.py

Tool which wrapps binary executable ARM images with ELF header. If a firmware
contains binary image of executable file, this tool can rebuild ELF header for it.
The ELF format can be then easily disassembled, as most debuggers can read ELF files.
Note that using this tool on encrypted firmwares will not result in useable ELF.

Example of converting FC firmware for *Phantom 3* to ELF:

```./arm_bin2elf.py -vv -e -b 0x8020000 -l 0x6000000 -p P3X_FW_V01.07.0060_m0306.bin```

The command above will cause the tool to try and detect where the border between
code (`.text`) and data (`.data`) sections should be. This detection is not perfect,
especially for binaries with no `.ARM.exidx` section between them. If `.ARM.exidx`
exists in the binary, the tool can easily find it and divide binary data properly,
treating `.ARM.exidx` as a separator between `.text` and `.data`.

In other words, position of the `.ARM.exidx` influences length of the `.text` section,
and starting offset of the `.data` section. If there is no `.ARM.exidx` section in
the file, it will still be used as separator, just with zero size.
After first look at the disassembly, it is good to check where the correct border
between `.text` and `.data` sections is located. Memory address of this location can
be used to generate better ELF file.

Additional updates to the ELF after first look can include defining `.bss` sections.
These sections represent uninitialized RAM and MMIO areasused by the binary. It is
tempting to just define one big section which covers whole memory map address range
according to programming guide of the chip, but that results in huge memory usage
and related slowdowns while disassembling the file, while also making the file harder
to navigate.

Note that all section offsets are defined using in-memory address, not the position
within BIN file. If you have found proper location of a section within BIN file,
remember to add base address to the file position before inserting to the command
line of this tool.

Base address can be often found in programming guide of the specific chip; sometimes it
may be shifted from that location, if the binary is loaded by an additional bootloader.
In such cases the bootloader takes the location from documentation, and the real firmware
binary is loaded at a bit higher base address.

Optimized examples for specific firmwares:

```./arm_bin2elf.py -vv -e -b 0x8020000 --section .ARM.exidx@0x80A5D34:0 --section .bss@0x10000000:0x0A000 --section .bss2@0x20000000:0x30000 --section .bss3@0x40000000:0x30000 -p P3X_FW_V01.07.0060_m0306.bin```

```./arm_bin2elf.py -vv -e -b 0x000A000 --section .ARM.exidx@0x026E50:0 --section .bss@0x10000000:0x08000 --section .bss2@0x40000000:0x50000 --section .bss3@0xE0000000:0x10000 -p C1_FW_V01.06.0000_m1400.bin```

```./arm_bin2elf.py -vv -e -b 0x000A000 --section .ARM.exidx@0x0212E0:0 --section .bss@0x10000000:0x08000 --section .bss2@0x40000000:0x50000 --section .bss3@0xE0000000:0x10000 -p C1_FW_v01.09.0200_m1400.bin```

```./arm_bin2elf.py -vv -e -b 0x000A000 --section .ARM.exidx@0x0233E0:0 --section .bss@0x02000000:0x04000 --section .bss2@0x2008000:0x1000 --section .bss3@0x1C000000:0x2400 --section .bss4@0x1c024000:0x2400 --section .bss5@0x4002C000:0x50000 --section .bss6@0x400F8000:0x200 --section .bss7@0xE000E000:0x1200 -p C1_FW_V01.06.0000_m1401.bin```

```./arm_bin2elf.py -vv -e -b 0x8008000 --section .ARM.exidx@0x8015510:0 --section .bss@0x1FFFF700:0x05A00 --section .bss2@0x40000000:0x6700 --section .bss3@0x40010000:0x5500 --section .bss4@0x40020000:0x2200 --section .bss5@0x42200000:0x100 --section .bss6@0x42420000:0x500 -p P3X_FW_V01.08.0080_m0900.bin```

```./arm_bin2elf.py -vv -e -b 0x8008000 --section .ARM.exidx@0x801B6D0:0 --section .bss@0x1FFFF700:0x0C900 --section .bss2@0x40000000:0x6700 --section .bss3@0x40010000:0x5500 --section .bss4@0x40020000:0x7000 --section .bss5@0x50060800:0x100 -p P3X_FW_V01.11.0030_m0400.bin```

```./arm_bin2elf.py -vv -e -b 0x0420000 --section .ARM.exidx@0x4EDAF0:0 --section .bss@0x20400000:0x40000 --section .bss4@0x42200000:0x100 -p MATRICE600_FW_V02.00.00.21_m0306.bin```

```./arm_bin2elf.py -vv -e -b 0x0420000 --section .ARM.exidx@0x4F0E00:0 --section .bss@0x20400000:0x60100 --section .bss2@0x400E0000:0x2000 -p wm330_0306_v03.01.10.93_20160707.fw_0306.decrypted.bin```

```./arm_bin2elf.py -vv -e -b 0x0420000 --section .ARM.exidx@0x5277d0:0 --section .bss@0x20400000:0x60000 --section .bss2@0x400E0000:0x1000 --section .bss3@0xE0000000:0x10000 -p wm100_0306_v03.02.43.20_20170920.pro.fw_0306.decrypted.bin```

```./arm_bin2elf.py -vv -e -b 0x0420000 --section .ARM.exidx@0x5465d8:0 --section .bss@0x20400000:0x60100 --section .bss2@0x400E0000:0x2000 -p wm220_0306_v03.02.35.05_20170525.pro.fw_0306.decrypted.bin```

```./arm_bin2elf.py -vv -e -b 0x7D000000 --section .ARM.exidx@0x7D0356E0:0 --section .bss@0x7D04f380:0x3800 --section .bss2@0x7D0f1900:0x200 -p wm230_0801_v10.00.07.12_20180126-recovery.img.TZOS.bin```

```./arm_bin2elf.py -vv -e -b 0xFFFC0000 --section .ARM.exidx@0xFFFDA540:0x20 --section .bss@0xFFFE14D0:0x42B0 --section .bss1@0x0202000:0x20 --section .bss2@0x0402020:0x20 --section .bss3@0x0B00000:0x40 --section .bss4@0x2700000:0x40 --section .bss5@0x9000000:0x20 --section .bss6@0xF0440000:0x4500 --section .bss7@0xF0501200:0x200 --section .bss8@0xF0A09000:0x20 --section .bss9@0xF0A40000:0x1200 --section .bss10@0xF0A4D000:0x2100 --section .bss11@0xF0A61000:0x1200 --section .bss12@0xF0A72000:0x20 --section .bss13@0xF0D02000:0x20 --section .bss14@0xF0D04000:0x20 --section .bss15@0xF0E00A00:0xC0 --section .bss16@0xF0E08000:0x20 --section .bss17@0xF5001000:0x40 --section .bss18@0xF6409000:0x100 --section .bss19@0xF6800000:0x1200 --section .bss20@0xFA800000:0x100 --section .bss21@0xFAF01000:0x3500 --section .bss22@0xFB001000:0x2900 --section .bss23@0xFCC01000:0x2400 --section .bss24@0xFD001000:0x2D00 --section .bss25@0xFD400000:0x20 --section .bss26@0xFD501000:0x2400 --section .bss27@0xFF001000:0x1100 -p wm230_0801_v10.00.07.12_20180126.pro.fw_0801.bootarea_p0_BLLK.bin```

This tool supports only conversion in direction of bin-to-elf. To convert an ELF
file back to BIN (ie. after modifications), use `objcopy` utility for the
specific architecture. The `objcopy` tool is a part of GNU Binary Utilities
(`binutils`) and not a part of this repository.

Examples:

```arm-none-eabi-objcopy -O binary P3X_FW_V01.07.0060_m0100_part_sys.elf P3X_FW_V01.07.0060_m0100_part_sys.bin```

```arm-none-eabi-objcopy -O binary P3X_FW_V01.07.0060_m0900.elf P3X_FW_V01.07.0060_m0900.bin```

### amba_sys2elf.py

Ambarella A7/A9 firmware "System Software" partition converter. The partition
contains a binary image of executable file, and this tool wraps it with ELF
header. The ELF format can be then easily disassembled, as most debuggers can
read ELF files. This tool is very similar to `arm_bin2elf.py`, it is just
pre-configured to specific firmware.

Example: ```./amba_sys2elf.py -vv -e -l 0x6000000 -p P3X_FW_V01.08.0080_m0100_part_sys.a9s```

All border adjusting rules explained for `arm_bin2elf.py` apply for this tool as well.

Optimized examples for specific firmwares:

```./amba_sys2elf.py -vv -e -l 0x6000000 --section .ARM.exidx@0xEA83E4C:0 -p P3X_FW_V01.08.0080_m0100_part_sys.a9s```

```./amba_sys2elf.py -vv -e -l 0x6000000 --section .ARM.exidx@0xEA82EC0:0 -p P3X_FW_V01.07.0060_m0100_part_sys.a9s```

```./amba_sys2elf.py -vv -e -l 0x6000000 --section .ARM.exidx@0xEA64774:0 -p P3X_FW_V01.01.0008_m0100_part_sys.a9s```

### amba_sys_hardcoder.py

Ambarella A7/A9 firmware "System Software" partition hard-coded values editor.

The tool can parse Ambarella firmware SYS partition converted to ELF.
It finds certain hard-coded values in the binary data, and allows
exporting or importing them. Only `setValue` element in the exported JSON file
is really changeable, all the other data is just informational.

Example of exporting hard-coded values to JSON file:

```./amba_sys_hardcoder.py -vv -x --elffile P3X_FW_V01.08.0080_m0100_part_sys.elf```

Example of importing values from JSON file back to ELF:

```./amba_sys_hardcoder.py -vv -u --elffile P3X_FW_V01.08.0080_m0100_part_sys.elf```

### dm3xx_encode_usb_hardcoder.py

Dji DM3xx DaVinci encode_usb binary hard-coded values editor.

The tool can parse encode_usb ELF file from Dji Firmware module for
TI DM3xx DaVinci Media Processor.
It finds certain hard-coded values in the binary data, and allows
exporting or importing them.

Example of exporting hard-coded values to JSON file:

```./dm3xx_encode_usb_hardcoder.py -vv -x --elffile P3X_FW_V01.07.0060_m0800-encode_usb.elf```

Example of importing values from JSON file back to ELF:

```./dm3xx_encode_usb_hardcoder.py -vv -u --elffile P3X_FW_V01.07.0060_m0800-encode_usb.elf```

### lightbridge_stm32_hardcoder.py

Dji Lightbridge STM32 micro-controller binary hard-coded values editor.

The tool can parse Lightbridge MCU firmware converted to ELF.
It finds certain hard-coded values in the binary data, and allows
exporting or importing them.

Example of exporting hard-coded values to JSON file:

```./lightbridge_stm32_hardcoder.py -vv -x --elffile P3X_FW_V01.07.0060_m0900.elf```

Example of importing values from JSON file back to ELF:

```./lightbridge_stm32_hardcoder.py -vv -u --elffile P3X_FW_V01.07.0060_m0900.elf```

### dji_flyc_hardcoder.py

Dji Flight Controller firmware binary hard-coded values editor.

The tool can parse Flight Controller firmware converted to ELF.
It finds certain hard-coded values in the binary data, and allows
exporting or importing them.

Example of exporting hard-coded values to JSON file:

```./dji_flyc_hardcoder.py -vvv -x -e P3X_FW_V01.07.0060_m0306.elf```

Example of importing values from JSON file back to ELF:

```./dji_flyc_hardcoder.py -vvv -u -e P3X_FW_V01.07.0060_m0306.elf```

### dji_flyc_param_ed.py

Flight Controller Firmware Parameters Array Editor finds an array of flight
parameters within firmware binary, and allows to extract the parameters to a JSON
format text file. This file can then easily be modified, and used to update
binary firmware, changing attributes and limits of each parameter.

In order to find the Parameters Array, the tool needs base address used for loading
the binary file into RAM of the micro-controller. If you don't know the base address
to use, programming guide of the specific chip used may give you clues.

Example of extracting and then updating the flight controller parameters:

```./dji_flyc_param_ed.py -vv -x -m P3X_FW_V01.07.0060_m0306.bin```

```./dji_flyc_param_ed.py -vv -u -m P3X_FW_V01.07.0060_m0306.bin```

More examples, for other products:

```./dji_flyc_param_ed.py -vv -x -b 0x420000 -m A3_FW_V01.02.00.00_m0306.bin```

```./dji_flyc_param_ed.py -vv -x -b 0x420000 -m MATRICE600_FW_V02.00.00.21_m0306.bin```

```./dji_flyc_param_ed.py -vv -x -b 0x420000 -m MATRICE600PRO_FW_V01.00.00.80_m0306.bin```

```./dji_flyc_param_ed.py -vv -x -b 0x420000 -m wm220_0306_v03.02.35.05_20170525.pro.bin```

```./dji_flyc_param_ed.py -vv -x -b 0x0000 -m wm230_0306_v01.00.02.255_20170213.bin```

### comm_dat2pcap.py

DJI Universal Packet Container stream pareser with pcap output format.

The script parses Raw DUML stream (ie. flight log files ```FLY???.DAT```) and wraps
single packets with PCap headers. Packets CRC is checked before the data is passed.
Any tool with PCap format support can then be used to analyse the data (ie. Wireshark).

Example of converting flight log file:

```./comm_dat2pcap.py -vv -d FLY002.DAT```

### comm_serial2pcap.py

DJI serial bus sniffer with DUML packetizer and PCap output format.

The script captures data from two UARTs and wraps single DUML packets with PCap headers.
Packets CRC is checked before the data is passed to the PCap file or FIFO pipe.
Any tool with pcap format support can then be used to analyse the data (ie. Wireshark).

The utility requires two serial interfaces with RX lines connected to RX and TX lines
within the drone.

Example of starting the capture from two UART-to-TTL (aka FTDI) converters:

```./comm_serial2pcap.py -b 115200 -F /tmp/wsf /dev/ttyUSB0 /dev/ttyUSB1```

### comm_mkdupc.py

DUML Packet Builder with hex string output.

This tool can build a proper DUML packet containing given header fields and payload.
The packet will be outputed in hexadecimal form. List of known commands and the look
of expected payloads can be found in Wireshark dissectors described below.

Example of generating a packet to ask Spark camera module for its Sensor ID:

```./comm_mkdupc.py --receiver_type=Camera --seq_num=65280 --ack_type=ACK_After_Exec --cmd_set=Camera --cmd_id=181```

### comm_serialtalk.py

DUML Builder which sends packet to DJI product and receives a response.

This tool builds a proper DUML packet containing given header fields and payload.
Then it sends it via given serial port and waits for response. It shows the
returning packet upon receiving it.

It can be considered an alternative to `dji_mb_ctrl` binary which can be found
in some drones. Parameter names are different between these two tools though.

Example of asking Flight Controller for hardware and firmware version data (tested on Ph3):

```./comm_serialtalk.py --port /dev/ttyUSB0 -vv --timeout=5000 --receiver_type=FlyController --seq_num=65280 --ack_type=No_ACK_Needed --cmd_set=General --cmd_id=1```

Example of asking Flight Controller for hardware and firmware version data (Mavic 3):

```./comm_serialtalk.py --bulk -vv --timeout=5000 --receiver_type=FlyController --seq_num=65280 --ack_type=ACK_After_Exec --cmd_set=General --cmd_id=1```

### comm_og_service_tool.py

OGs Service Tool for Dji products.

The script allows to trigger a few service functions of Dji drones. It talks to the drone
like `comm_serialtalk.py`, but provides easier interface for some important functions.

Example of listing Flight Controller Parameters 200-300 on Ph3 Pro to CSV format:

```./comm_og_service_tool.py --port /dev/ttyUSB0 P3X FlycParam list --start=200 --count=100 --fmt=csv```

Example of getting value of Flight Controller Parameters on Spark:

```./comm_og_service_tool.py --port /dev/ttyUSB0 -vv SPARK FlycParam get g_config.flying_limit.max_height_0 --fmt=2line```

Example of setting value of Flight Controller Parameters on Spark:

```./comm_og_service_tool.py --port /dev/ttyUSB0 -vv SPARK FlycParam set g_config.flying_limit.max_height_0 500```

Example of performing service "joint coarse" calibration of Spark gimbal:

```./comm_og_service_tool.py --port /dev/ttyUSB0 -vv SPARK GimbalCalib JointCoarse```

Example of performing service "linear hall" calibration of Spark gimbal, using Windows host:

```python3 comm_og_service_tool.py --port COM23 -vv SPARK GimbalCalib LinearHall```

Example of listing Flight Controller Parameters 200-300 on the Mavic 3 Pro to CSV format:

```./comm_og_service_tool.py --bulk MAV3 FlycParam list --start=200 --count=100 --fmt=csv```

### comm_sbs_bqctrl.py

Smart Battery System communication tool.

This tool allows to interact with chips designed based on Smart Battery Data
Specification. It also supports some extensions to that specification
implemented by Texas Instruments in their BQ series gas gauge chips.

Usage of this tool requires connection to SMBus lines (SDA,SCL,GND) of the
SBS-compatible chip. SMBus communication uses I2C as a base, so most devices
with I2C bus can be used to establish the communication.

Example of simple read of BatteryStatus(), using I2C interface (the script will construct SMBus messages internally):

```./comm_sbs_bqctrl.py -vvv --bus "i2c:1" --dev_address 0x0b read BatteryStatus```

Example of reading several flag fields from BQ30z55 by ManufacturerAccess(), using SMBus interface:

```./comm_sbs_bqctrl.py -v --bus "smbus:1" --dev_address 0x0b --chip BQ30z55 --short monitor BQStatusBitsMA```

Example of unsealing BQ30z55 (enabling write capabilities), with default SHA-1 key, using I2C interface on 2nd bus device available to OS:

```./comm_sbs_bqctrl.py -v --bus "i2c:2" --dev_address 0x0b --chip BQ30z55 --short sealing Unseal```

### tests

The `tests` folder contains a collection of scripts which can be used to verify
whether the tools do their job correctly. Most tests will extract and re-pack
a firmware found in `fw_packages` directory, then compare the result to original
to check whether no unintended changes were introduced to the file.
Tools which communicate to a product are tested by injecting expected answers
to their receive buffers, so they can be tested without the product as well.

Besides testing your modifications, you can also use tests as source of more
usage examples of the tools. They contain command lines to extract specific
firmwares and execute specific commands on the products.

There are `bash` and `pytest` tests, covering the same general functionalities.

Example of executing the `pytest` tests:

```pytest tests -rsx --full-scope -o log_cli=true --log-cli-level=INFO```

The `--full-scope` option makes the tests execute on all known binaries, rather
that on a selection used for continous integration. The CI tests are selective
to make sure the automatic testing ends in reasonable time.

### comm_dissector

The folder contains [Wireshark](https://www.wireshark.org/) dissector for for analyzing
communication in DJI drone interfaces.

Documentation of the tool is [included in its folder](comm_dissector/README.md).

# Symbols

For some specific firmware modules in specific versions, there are partial symbols
available in 'symbols' directory. The symbols are in two formats:

- MAP files - Can be loaded into most disassemblers with minimal effort. For IDA Pro,
there is a plugin which can read MAP files and rename functions and variables
accordingly. Only functions and global variables which were given a meaningful names
are included in these files.
- IDC script - Format specific to IDA Pro. Stores not only functions and globals,
but also type information - enums and structs. Allows storing function parameters
and local variables with their names and types, too. Can be easily applied to an
opened ELF file via IDA Pro, no other tool will understand it.

Symbols are matched with ELF files generated with the tools described above,
not directly with the BINs. Use example commands provided in previous section
to generate ELF files with content matching to the symbols.

When working on a firmware version for which no symbols are available, you may
want to use a version with symbols for reference in naming.

If you are looking for a best FW version for reference symbols, or you do not care
for FW versions at all and just want the most complete symbols - check size of MAP
file. MAP file mostly contains manually-named symbols, so the largest one will be
for firmware version on which more reversing work was done.
