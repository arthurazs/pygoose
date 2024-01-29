import datetime as dt
import decimal as dec
from dataclasses import dataclass
from struct import pack, unpack
from typing import NamedTuple

from pygoose.datatypes.time_quality import TimeQuality

FRACTION_BYTES_SIZE = 3


class NegativeEpochError(ValueError): ...


class EpochTooBigError(ValueError): ...


class FractionBadSizeError(ValueError): ...


@dataclass(frozen=True, slots=True)
class FractionOfSeconds:
    value: dec.Decimal

    def __post_init__(self: "FractionOfSeconds") -> None:
        if self.value >= dec.Decimal(1):
            msg = "too big"
            raise FractionBadSizeError(msg)
        if self.value < dec.Decimal(0):
            msg = "negative"
            raise FractionBadSizeError(msg)

    @staticmethod
    def _fraction_sum(integer: int) -> dec.Decimal:
        acc = dec.Decimal(0)
        for i in range(24):
            b = 1 if integer & (2 ** (23 - i)) > 0 else 0
            acc += dec.Decimal(b) * dec.Decimal(2 ** -(i + 1))
        return acc

    @classmethod
    def from_bytes(cls: type["FractionOfSeconds"], bytestring: bytes) -> "FractionOfSeconds":
        return cls(value=cls._fraction_sum(unpack("!L", b"\x00" + bytestring)[0]))

    def __int__(self: "FractionOfSeconds") -> int:
        # TODO @arthurazs: important? should only have .value? or bin repr important too?
        integer = 0
        acc = dec.Decimal()
        for i in range(24):
            temp = acc + dec.Decimal(2 ** (-(i + 1)))
            if temp <= self.value:
                integer += 2 ** (23 - i)
                acc = temp
        return integer

    def __bytes__(self: "FractionOfSeconds") -> bytes:
        return pack("!L", int(self))[1:]


@dataclass(frozen=True, kw_only=True, slots=True)
class TimeStamp:
    # 61850-7-2, 2nd ed., 6.1.2.9
    second_since_epoch: int  # u32
    fraction_bytes: bytes  # u24
    time_quality: "TimeQuality"

    def __post_init__(self: "TimeStamp") -> None:
        if self.second_since_epoch < 0:
            raise NegativeEpochError
        if self.second_since_epoch > 0xFFFFFFFF:
            raise EpochTooBigError
        if len(self.fraction_bytes) != 3:
            raise FractionBadSizeError

    @classmethod
    def default(
            cls: type["TimeStamp"],
            second_since_epoch: int = 0,
            fraction_bytes: bytes = b"\x00\x00\x00",
            time_quality: "TimeQuality | None" = None,
    ) -> "TimeStamp":
        if time_quality is None:
            time_quality = TimeQuality.default()
        return cls(second_since_epoch=second_since_epoch, fraction_bytes=fraction_bytes, time_quality=time_quality)

    def fraction_of_second(self: "TimeStamp") -> dec.Decimal:
        value = dec.Decimal(0)
        integer = unpack("!L", b"\x00" + self.fraction_bytes)[0]
        for i in range(24):
            b = 1 if integer & (2 ** (23 - i)) > 0 else 0
            value += dec.Decimal(b) * dec.Decimal(2 ** -(i + 1))
        return value


class Timestamp(NamedTuple):
    # 61850-7-2, 2nd ed., 6.1.2.9
    second_since_epoch: int  # u32
    fraction_of_second: int  # u24, nanoseconds
    time_quality: "TimeQuality"

    @staticmethod
    def bin2nano(bin_fraction: str) -> int:
        """Returns the sum from the binary bin_fraction in nanoseconds."""
        acc = dec.Decimal()
        for i, bi in enumerate(bin_fraction):
            acc += (bi == "1") * (dec.Decimal(2 ** (-(i + 1))))
        return int(acc * dec.Decimal(1e9))

    @classmethod
    def int2nano(cls: type["Timestamp"], fraction: int) -> int:
        """Returns the parsed representation for the fraction in nanoseconds."""
        list_fraction = []
        acc = dec.Decimal()
        d_fraction = fraction * 1e-9
        for i in range(24):
            temp = acc + dec.Decimal(2 ** (-(i + 1)))
            if temp > d_fraction:
                list_fraction.append("0")
            else:
                list_fraction.append("1")
                acc = temp
        return cls.bin2nano("".join(list_fraction))

    def datetime(self: "Timestamp") -> dt.datetime:
        return dt.datetime.fromtimestamp(self.second_since_epoch) + dt.timedelta(
            microseconds=self.fraction_of_second / 1e3,
        )

    @classmethod
    def unpack(cls: type["Timestamp"], bytes_string: bytes) -> "Timestamp":
        """Returns the timestamp unpacked from bytes."""
        # IEC 61850 7-2
        epoch_s = unpack("!L", bytes_string[:4])[0]
        i_fraction = unpack("!L", b"\x00" + bytes_string[4:7])[0]
        b_fraction = f"{i_fraction:024b}"
        fraction_ns = cls.bin2nano(b_fraction)

        quality = TimeQuality.from_bytes(bytes_string[7:])
        return cls(
            second_since_epoch=epoch_s,
            fraction_of_second=fraction_ns,
            time_quality=quality,
        )

    def __bytes__(self: "Timestamp") -> bytes:
        epoch = pack("!L", self.second_since_epoch)
        fraction = pack("!L", self.int2nano(self.fraction_of_second))[1:]
        quality = bytes(self.time_quality)
        return epoch + fraction + quality
