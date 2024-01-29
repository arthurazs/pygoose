from dataclasses import dataclass
from struct import pack, unpack

UNSPECIFIED_ACCURACY = 31
MAX_SPECIFIED_ACCURACY = 24
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
    accuracy: int  # TODO @arthurazs: What's the relationship between fraction and accuracy

    def __post_init__(self: "TimeQuality") -> None:
        if self.accuracy > MAX_SPECIFIED_ACCURACY and self.accuracy != UNSPECIFIED_ACCURACY:
            raise InvalidAccuracyError(self.accuracy)

    @classmethod
    def default(
            cls: type["TimeQuality"], leap_second_known: bool = True, clock_failure: bool = False,  # noqa: FBT001, FBT002
            clock_not_sync: bool = False, accuracy: int = DEFAULT_ACCURACY,  # noqa: FBT001, FBT002
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
            accuracy=accuracy,
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

    def __int__(self: "TimeQuality") -> int:
        leap = self.leap_second_known << 7
        failure = self.clock_failure << 6
        sync = self.clock_not_sync << 5
        return leap + failure + sync + self.accuracy

    def __bytes__(self: "TimeQuality") -> bytes:
        return pack("!B", int(self))

    def debug(self: "TimeQuality") -> str:
        leap_sec = f"Leap second {'' if self.leap_second_known else 'un'}known"
        failure = f"Clock {'failure' if self.clock_failure else 'ok'}"
        sync = f"Clock{' not' if self.clock_not_sync else ''} synchronised"
        if self.accuracy == UNSPECIFIED_ACCURACY:
            return f"{leap_sec}, {failure}, {sync}, {self.accuracy} bits accuracy [unspecified behaviour]"
        return f"{leap_sec}, {failure}, {sync}, {self.accuracy} bits accuracy [{2**(-self.accuracy)} seconds accuracy]"

