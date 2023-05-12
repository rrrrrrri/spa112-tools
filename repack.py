"""
Copyright (C) 2023  CataLpa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import hashlib

os.system("dd if=ori.bin of=sqfs.ori bs=1 skip=1573256")    # extract sqfs
os.system("sudo ./tools/unsquashfs ./sqfs.ori")             # unpack squashfs
os.system("sudo cp ./files/rc.init.1 ./squashfs-root/etc")  # move init script to /etc
os.system("sudo chmod 777 ./squashfs-root/etc/rc.init.1")
os.system("sudo ./tools/mksquashfs ./squashfs-root ./target/target.image -check_data -noappend -le -noI -all-root")   # repack
os.system("sudo ./tools/mkimage -A arm -O linux -C none -T filesystem -n SP2Xcybertan_rom_bin -c SP2X -d ./target/target.image -s ./target/file_system.img")    # pack to uimage

f = open("./target/file_system.img", "rb")
data = f.read()
f.close()
t = open("./target/padding_file_system.img", "wb")
t_data = data + b"\x00" * 40960    # padding \x00
t.write(t_data)
t.close()

os.system("cp ./target/kernel_mdu.bin.ori ./target/kernel_mdu.bin")
os.system("cat ./target/padding_file_system.img >> ./target/kernel_mdu.bin")
os.system("./tools/moduler -v 1.0 -t 1 -i 0 -m 0x1200000 -o ./target/kernel_pfmwr.img ./target/kernel_mdu.bin")
os.system("./tools/pkger -v \"1.4.2\" -o ./target/packed.bin ./target/kernel_pfmwr.img")

f = open("./target/packed.bin", "rb")
tmp_data = f.read()
tmp_header = tmp_data[:0x104]
next_data = tmp_data[0x104:]
f.close()

fixed_header = tmp_header[:0x30] + b"\x00" * 0x20 + b"\x00\x00\x00\x88" + b"\x00\x00\x00\x80" + b"\x00\x9a\x01\x88" + b"\x31\x2e\x34\x2e" + tmp_header[0x60:0x84] + b"\x01\xea\xea\x3a" + tmp_header[0x84:]

i = 0
token = 0
buf = []
while i < len(fixed_header):
    buf.append((fixed_header[i] + token) & 0xff)
    token += 19
    i += 1

tmp = hashlib.md5(bytes(buf)).hexdigest()
fixed_header = tmp_header[:0x30] + b"\x00" * 0x10 + bytes.fromhex(tmp) + b"\x00\x00\x00\x88" + b"\x00\x00\x00\x80" + b"\x00\x9a\x01\x88" + b"\x31\x2e\x34\x2e" + tmp_header[0x60:0x84] + b"\x01\xea\xea\x3a" + tmp_header[0x84:]

tmp2 = hashlib.md5(fixed_header).hexdigest()
fixed_header = tmp_header[:0x30] + bytes.fromhex(tmp2) + bytes.fromhex(tmp) + b"\x00\x00\x00\x88" + b"\x00\x00\x00\x80" + b"\x00\x9a\x01\x88" + b"\x31\x2e\x34\x2e" + tmp_header[0x60:0x84] + b"\x01\xea\xea\x3a" + tmp_header[0x84:]

f = open("./target/final.img", "wb")
f.write(fixed_header + next_data)
f.close()

os.system("sudo rm -rf ./squashfs-root ./target/target.image")
os.system("rm -rf ./target/kernel_mdu.bin")
os.system("sudo rm -rf ./target/file_system.img")
os.system("rm -rf ./target/padding_file_system.img")
os.system("rm -rf ./target/kernel_pfmwr.img")
os.system("rm -rf ./target/packed.bin")