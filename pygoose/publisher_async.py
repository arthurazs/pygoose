import asyncio
import pathlib
import socket
from struct import pack as s_pack, unpack as s_unpack
import sys
from contextlib import suppress
from typing import TYPE_CHECKING
from itertools import count
import datetime as dt
from time import time_ns

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from typing import Iterator, Sequence


def get_sample() -> "Iterator[Sequence[str]]":
    path = pathlib.Path("data") / "example1.csv"
    with open(path, "r") as csv:
        csv.readline()
        for _ in range(2400):
            data = csv.readline()
            yield data.strip().split(",")


def triplet(identifier: bytes, value: bytes) -> bytes:
    length = len(value)
    if length < 0x80:
        return identifier + s_pack('!B', length) + value
    elif length <= 0xFF:
        return identifier + s_pack('!BB', 0x81, length) + value
    elif length <= 0xFFFF:
        return identifier + s_pack('!BH', 0x82, length) + value
    elif length <= 0xFFFFFF:
        return identifier + s_pack('!B', 0x83) + s_pack('!I', length)[1:] + value
    raise ValueError('Value too big')

def count_fraction(fraction):
    acc = 0
    for i, bi in enumerate(fraction):
        acc += int(bi) * (2 ** (-(i+1)))
    return acc

def timestamp():
    now = str(time_ns())
    epoch = int(now[:-9])
    fraction = f'{int(now[-9:][:-1]):024b}'
    # TODO calc 0.fraction, not fraction
    acc = count_fraction(fraction)
    print(int(fraction, 2), acc)
    # Value = SUM from i=0 to 23 of bi*2**–(i+1); Order = b0, b1, b2, b3, ...


def unpack_t(value=b"\x63\x5a\xe0\xa0\xf5\x8e\x21\x92"):
    epoch = dt.datetime.fromtimestamp(s_unpack('!L', value[:4])[0])
    fraction = s_unpack('!L', b"\x00" + value[4:7])[0]
    b_fraction = f'{fraction:024b}'
    new_fraction = f'{count_fraction(b_fraction):.9f}'
    print(f"{epoch}.{new_fraction[2:]}")
    # TODO unpack TimeQuality (61850-7-2)


def get_goose() -> "Iterator[bytes]":
    dst_addr = b"\x01\x0c\xcd\x01\x00\x01"
    src_addr = b"\x00\x30\xa7\x22\x9d\x01"
    goose_ether = b"\x88\xb8"
    app_id = b"\x00\x00"
    length = b"\x00\x74"  # TODO calc?
    reserved = b"\x00\x00\x00\x00"
    goose_type = b"\x61"
    goose_len = b"\x6a"  # TODO calc?
    gocb_ref = b"\x80\x1bSEL_421_SubCFG/LLN0$GO$PIOC"
    time_allowed_to_live = b"\x81\x02\x07\xd0"
    dat_set = b"\x82\x18SEL_421_SubCFG/LLN0$PIOC"
    go_id = b"\x83\x0bSEL_421_Sub"

    data_bool = triplet(b"\x83", b"\x00")
    data = triplet(b"\xab", data_bool)
    num_dat_set_entries = triplet(b"\x8a", b"\x01")

    nds_com = triplet(b"\x89", b"\x00")
    conf_rev = triplet(b"\x88", b"\x01")
    test = triplet(b"\x87", b"\x00")

    sq_num = b"\x86\x01\x01"
    st_num = b"\x85\x01\x01"
    t = b"\x84\x08\x63\x5a\xe0\xa0\xf5\x8e\x21\x92"

    goose = dst_addr + src_addr + goose_ether + app_id + length + reserved + goose_type + goose_len + gocb_ref + time_allowed_to_live + dat_set + go_id + t + st_num + sq_num + test + conf_rev + nds_com + num_dat_set_entries + data
    print(len(goose))
    # sq_num = 1
    # st_num = 1
    # t = 0
    for _ in range(10):
        yield goose


async def run(loop: "AbstractEventLoop", send: bool) -> None:
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0xB888) as nic:
        nic.bind(("lo", 0))
        nic.setblocking(False)

        if send:
            for goose in get_goose():
                await loop.sock_sendall(nic, goose)
                await asyncio.sleep(.05)
                print('sent...')
        else:
            for counter in count(1):
                elapsed = loop.time()
                data = await loop.sock_recv(nic, 1518)
                print(f"{counter}: {(loop.time() - elapsed) * 1_000:.3f} ms | {data[:20]}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    with suppress(KeyboardInterrupt):
        loop.run_until_complete(run(loop, sys.argv[1] == "0"))
    loop.close()
