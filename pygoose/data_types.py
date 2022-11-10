import datetime as dt
import decimal as dec
from struct import pack as s_pack
from struct import unpack as s_unpack
from typing import NamedTuple


def u32_bytes(value: int) -> bytes:
    return s_pack("!H", value)


def mac2bytes(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", "").replace("-", ""))


def ether2bytes(value: str) -> bytes:
    return bytes.fromhex(value)


class TimeQuality(NamedTuple):
    # TODO Change to pydantic.BaseModel?
    leap_second_know: bool
    clock_failure: bool
    clock_not_sync: bool
    accuracy: int  # TODO What's the relationship between fraction and accuracy

    @classmethod
    def unpack(cls, bytes_string: bytes) -> "TimeQuality":
        i_quality = s_unpack("!B", bytes_string)[0]
        b_quality = f"{i_quality:08b}"

        return cls(
            leap_second_know=b_quality[0] == "1",
            clock_failure=b_quality[1] == "1",
            clock_not_sync=b_quality[2] == "1",
            accuracy=int(b_quality[3:], 2),
        )

    def __bytes__(self) -> bytes:
        leap = "1" if self.leap_second_know else "0"
        failure = "1" if self.clock_failure else "0"
        sync = "1" if self.clock_not_sync else "0"
        accuracy = f"{self.accuracy:05b}"
        return s_pack("!B", int(leap + failure + sync + accuracy, 2))


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
    def int2nano(cls, fraction: int) -> int:
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

    def datetime(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.second_since_epoch) + dt.timedelta(
            microseconds=self.fraction_of_second / 1e3
        )

    @classmethod
    def unpack(cls, bytes_string: bytes) -> "Timestamp":
        """Returns the timestamp unpacked from bytes."""
        # IEC 61850 7-2
        epoch_s = s_unpack("!L", bytes_string[:4])[0]
        i_fraction = s_unpack("!L", b"\x00" + bytes_string[4:7])[0]
        b_fraction = f"{i_fraction:024b}"
        fraction_ns = cls.bin2nano(b_fraction)

        quality = TimeQuality.unpack(bytes_string[7:])
        return cls(
            second_since_epoch=epoch_s,
            fraction_of_second=fraction_ns,
            time_quality=quality,
        )

    def __bytes__(self) -> bytes:
        epoch = s_pack("!L", self.second_since_epoch)
        fraction = s_pack("!L", self.int2nano(self.fraction_of_second))[1:]
        quality = bytes(self.time_quality)
        return epoch + fraction + quality
