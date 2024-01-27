import datetime as dt
import decimal as dec
from struct import pack, unpack
from typing import NamedTuple
from dataclasses import dataclass


UNSPECIFIED_ACCURACY = 31
LEAP_SECONDS_KNOWN_BITS = 0b1000_0000
CLOCK_FAILURE_BITS = 0b0100_0000
CLOCK_NOT_SYNC_BITS = 0b0010_0000
ACCURACY_BITS = 0b0001_1111
DEFAULT_ACCURACY = 7  # 10ms accuracy (performance class T0)


class InvalidAccuracyError(ValueError): ...


@dataclass(frozen=True, kw_only=True, slots=True)
class TimeQuality:
    # 61850-7-2, 2nd ed., 6.1.2.9.3.3
    # 61850-8-1, 2nd ed., 8.1.3.7
    leap_second_known: bool
    clock_failure: bool
    clock_not_sync: bool
    accuracy: int  # TODO What's the relationship between fraction and accuracy

    def __post_init__(self: "TimeQuality") -> None:
        if self.accuracy > 24 and self.accuracy != UNSPECIFIED_ACCURACY:
            raise InvalidAccuracyError(self.accuracy)

    @classmethod
    def default(
            cls: type["TimeQuality"], leap_second_known: bool = True, clock_failure: bool = False,
            clock_not_sync: bool = False, accuracy: int = DEFAULT_ACCURACY
    ) -> "TimeQuality":
        """Creates a TimeQuality with default values.

        Leap second known
        Clock ok
        Clock sync
        Accuracy of 7 bits (10ms accuracy, performance class T0)
        """
        return cls(
            leap_second_known=leap_second_known,
            clock_failure=clock_failure,
            clock_not_sync=clock_not_sync,
            accuracy=accuracy
        )

    @classmethod
    def from_bytes(cls: type["TimeQuality"], bytes_string: bytes) -> "TimeQuality":
        quality = unpack("!B", bytes_string)[0]
        return cls(
            leap_second_known=(quality & LEAP_SECONDS_KNOWN_BITS) == LEAP_SECONDS_KNOWN_BITS,
            clock_failure=(quality & CLOCK_FAILURE_BITS) == CLOCK_FAILURE_BITS,
            clock_not_sync=(quality & CLOCK_NOT_SYNC_BITS) == CLOCK_NOT_SYNC_BITS,
            accuracy=quality & ACCURACY_BITS,
        )

    def __bytes__(self: "TimeQuality") -> bytes:
        leap = self.leap_second_known << 7
        failure = self.clock_failure << 6
        sync = self.clock_not_sync << 5
        return pack("!B", leap + failure + sync + self.accuracy)

    def debug(self: "TimeQuality") -> str:
        leap_sec = f"Leap second {'' if self.leap_second_known else 'un'}known"
        failure = f"Clock {'failure' if self.clock_failure else 'ok'}"
        sync = f"Clock{' not' if self.clock_not_sync else ''} synchronised"
        if self.accuracy == UNSPECIFIED_ACCURACY:
            return f"{leap_sec}, {failure}, {sync}, {self.accuracy} bits accuracy [unspecified behaviour]"
        return f"{leap_sec}, {failure}, {sync}, {self.accuracy} bits accuracy [{2**(-self.accuracy)} seconds accuracy]"


class Timestamp(NamedTuple):
    second_since_epoch: int
    fraction_of_second: int  # nanoseconds
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
            microseconds=self.fraction_of_second / 1e3
        )

    @classmethod
    def unpack(cls: type["Timestamp"], bytes_string: bytes) -> "Timestamp":
        """Returns the timestamp unpacked from bytes."""
        # IEC 61850 7-2
        epoch_s = unpack("!L", bytes_string[:4])[0]
        i_fraction = unpack("!L", b"\x00" + bytes_string[4:7])[0]
        b_fraction = f"{i_fraction:024b}"
        fraction_ns = cls.bin2nano(b_fraction)

        quality = TimeQuality.unpack(bytes_string[7:])
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
