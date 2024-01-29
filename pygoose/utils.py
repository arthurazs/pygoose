import decimal as dec
from asyncio import sleep
from time import time_ns
from typing import TYPE_CHECKING
from struct import pack

from pygoose.asn1 import Triplet
from pygoose.datatypes.time_stamp import Timestamp

if TYPE_CHECKING:
    from pygoose.datatypes import TimeQuality


def u32_bytes(value: int) -> bytes:
    return pack("!H", value)


def mac2bytes(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", "").replace("-", ""))


def _bytes2hex(bytes_string: bytes) -> str:
    return bytes_string.hex()


def bytes2mac(bytes_string: bytes) -> str:
    mac = _bytes2hex(bytes_string)
    return ":".join(mac[index : index + 2] for index in range(0, len(mac), 2)).upper()


def bytes2hexstring(bytes_string: bytes) -> str:
    return "0x" + _bytes2hex(bytes_string).upper()


def bytes2string(bytes_string: bytes) -> str:
    return bytes_string.decode("utf8")


def bytes2u16(bytes_string: bytes) -> int:
    return s_unpack("!H", bytes_string)[0]  # type: ignore[no-any-return]


bytes2ether = bytes2hexstring


def ether2bytes(value: str) -> bytes:
    return bytes.fromhex(value)


def now(quality: "TimeQuality") -> Triplet:
    current_time = dec.Decimal(time_ns()) * dec.Decimal(1e-9)
    epoch = int(current_time)
    fraction = int((current_time % 1) * int(1e9))
    timestamp = Timestamp(
        second_since_epoch=epoch, fraction_of_second=fraction, time_quality=quality
    )
    return Triplet(0x84, bytes(timestamp))


def usleep(microseconds: float) -> None:
    # TODO do not use busy wait?
    end = time_ns() + (microseconds * 1e3)
    while True:
        if time_ns() >= end:
            break


async def async_usleep(microseconds: float) -> None:
    # TODO do not use busy wait?
    end = time_ns() + (microseconds * 1e3)
    while True:
        await sleep(0)
        if time_ns() >= end:
            break
