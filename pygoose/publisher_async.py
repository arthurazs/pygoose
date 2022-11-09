import asyncio
import decimal as dec
import pathlib
import socket
from struct import pack as s_pack, unpack as s_unpack
import sys
from contextlib import suppress
from typing import NamedTuple, TYPE_CHECKING
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


class TimeQuality(NamedTuple):
    # TODO Change to pydantic.BaseModel?
    leap_second_know: bool
    clock_failure: bool
    clock_not_sync: bool
    accuracy: int  # TODO What's the relationship between fraction and accuracy

    @classmethod
    def unpack(cls, bytes_string) -> "TimeQuality":
        i_quality = s_unpack('!B', bytes_string)[0]
        b_quality = f'{i_quality:08b}'

        return cls(
            leap_second_know=b_quality[0] == '1',
            clock_failure=b_quality[1] == '1',
            clock_not_sync=b_quality[2] == '1',
            accuracy=int(b_quality[3:], 2)
        )

    def __bytes__(self) -> bytes:
        leap = '1' if self.leap_second_know else '0'
        failure = '1' if self.clock_failure else '0'
        sync = '1' if self.clock_not_sync else '0'
        accuracy = f'{self.accuracy:05b}'
        return s_pack('!B', int(leap + failure + sync + accuracy, 2))


class Timestamp(NamedTuple):
    second_since_epoch: int
    fraction_of_second: int  # nanoseconds
    time_quality: "TimeQuality"


    @staticmethod
    def bin2nano(bin_fraction: str) -> int:
        """Returns the sum from the binary bin_fraction in nanoseconds."""
        acc = dec.Decimal()
        for i, bi in enumerate(bin_fraction):
            acc += (bi == '1') * (dec.Decimal(2 ** (-(i + 1))))
        return int(acc * dec.Decimal(1E9))

    @classmethod
    def int2nano(cls, fraction: int) -> int:
        """Returns the parsed representation for the fraction in nanoseconds."""
        list_fraction = []
        acc = dec.Decimal()
        d_fraction = fraction * 1E-9
        for i in range(24):
            temp = acc + dec.Decimal(2 ** (- (i + 1)))
            if temp > d_fraction:
                list_fraction.append('0')
            else:
                list_fraction.append('1')
                acc = temp
        return cls.bin2nano(''.join(list_fraction))

    def datetime(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.second_since_epoch) + \
               dt.timedelta(microseconds=self.fraction_of_second / 1E3)

    @classmethod
    def unpack(cls, bytes_string: bytes) -> "Timestamp":
        """Returns the timestamp unpacked from bytes."""
        # IEC 61850 7-2
        epoch_s = s_unpack('!L', bytes_string[:4])[0]
        i_fraction = s_unpack('!L', b"\x00" + bytes_string[4:7])[0]
        b_fraction = f'{i_fraction:024b}'
        fraction_ns = cls.bin2nano(b_fraction)

        quality = TimeQuality.unpack(bytes_string[7:])
        return cls(second_since_epoch=epoch_s, fraction_of_second=fraction_ns, time_quality=quality)

    def __bytes__(self) -> bytes:
        epoch = s_pack('!L', self.second_since_epoch)
        fraction = s_pack('!L', self.int2nano(self.fraction_of_second))
        quality = bytes(self.time_quality)
        return epoch + fraction + quality


def new_datetime(quality: TimeQuality) -> bytes:
    now = dec.Decimal(time_ns()) * dec.Decimal(1E-9)
    epoch = int(now)
    fraction = int((now % 1) * int(1E9))
    return bytes(Timestamp(second_since_epoch=epoch, fraction_of_second=fraction, time_quality=quality))


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

    sq_num = triplet(b"\x86", b"\x01")  # changes to 0
    st_num = triplet(b"\x85", b"\x01")

    quality = TimeQuality(leap_second_know=True, clock_failure=False, clock_not_sync=False, accuracy=18)
    t = new_datetime(quality)

    for index in range(10):
        goose = dst_addr + src_addr + goose_ether + app_id + length + reserved + goose_type + goose_len + gocb_ref + time_allowed_to_live + dat_set + go_id + t + st_num + sq_num + test + conf_rev + nds_com + num_dat_set_entries + data
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
