import decimal as dec
from asyncio import sleep
from time import time_ns
from typing import TYPE_CHECKING

from pygoose.asn1 import Triplet
from pygoose.data_types import DEFAULT_QUALITY, Timestamp

if TYPE_CHECKING:
    from pygoose.data_types import TimeQuality


def now(quality: "TimeQuality" = DEFAULT_QUALITY) -> Triplet:
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
