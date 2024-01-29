import pytest

import pygoose.datatypes.time_quality as tq


class TestLeapFailureSync:
    def test_default(self: "TestLeapFailureSync") -> None:
        # 0b1000_0111
        time_quality = tq.TimeQuality.default()
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == tq.DEFAULT_ACCURACY
        assert int(time_quality) == 0x87
        assert bytes(time_quality) == b"\x87"

    # t t t
    def test_true_true_true(self: "TestLeapFailureSync") -> None:
        # 0b1110_0000
        time_quality = tq.TimeQuality(leap_second_known=True, clock_failure=True, clock_not_sync=True, accuracy=0)
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xE0
        assert bytes(time_quality) == b"\xE0"

    # t t f
    def test_true_true_false(self: "TestLeapFailureSync") -> None:
        # 0b1100_0000
        time_quality = tq.TimeQuality(leap_second_known=True, clock_failure=True, clock_not_sync=False, accuracy=0)
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xC0
        assert bytes(time_quality) == b"\xC0"

    # t f t
    def test_true_false_true(self: "TestLeapFailureSync") -> None:
        # 0b1010_0000
        time_quality = tq.TimeQuality(leap_second_known=True, clock_failure=False, clock_not_sync=True, accuracy=0)
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xA0
        assert bytes(time_quality) == b"\xA0"

    # t f f
    def test_true_false_false(self: "TestLeapFailureSync") -> None:
        # 0b1000_0000
        time_quality = tq.TimeQuality(leap_second_known=True, clock_failure=False, clock_not_sync=False, accuracy=0)
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x80
        assert bytes(time_quality) == b"\x80"

    # f t t
    def test_false_true_true(self: "TestLeapFailureSync") -> None:
        # 0b0110_0000
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=True, clock_not_sync=True, accuracy=0)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x60
        assert bytes(time_quality) == b"\x60"

    # f t f
    def test_false_true_false(self: "TestLeapFailureSync") -> None:
        # 0b0100_0000
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=True, clock_not_sync=False, accuracy=0)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x40
        assert bytes(time_quality) == b"\x40"

    # f f t
    def test_false_false_true(self: "TestLeapFailureSync") -> None:
        # 0b0010_0000
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=True, accuracy=0)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x20
        assert bytes(time_quality) == b"\x20"

    # f f f
    def test_false_false_false(self: "TestLeapFailureSync") -> None:
        # 0b0000_0000
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=0)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x00
        assert bytes(time_quality) == b"\x00"


class TestAccuracy:
    def test_unspecified_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1111
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False,
                            accuracy=tq.UNSPECIFIED_ACCURACY)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == tq.UNSPECIFIED_ACCURACY
        assert int(time_quality) == 0x1F
        assert bytes(time_quality) == b"\x1F"

    def test_min_accuracy(self: "TestAccuracy") -> None:
        # 0b0000_0001
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=1)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 1
        assert int(time_quality) == 0x01
        assert bytes(time_quality) == b"\x01"

    def test_max_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1000
        time_quality = tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=24)
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 24
        assert int(time_quality) == 0x18
        assert bytes(time_quality) == b"\x18"

    def test_min_invalid_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1001
        with pytest.raises(tq.InvalidAccuracyError) as exc_info:
            tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=25)
        exc_info.match("25")

    def test_max_invalid_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1110
        with pytest.raises(tq.InvalidAccuracyError) as exc_info:
            tq.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=30)
        exc_info.match("30")


class TestFromBytes:
    def test_default(self: "TestFromBytes") -> None:
        # 0b1000_0111
        time_quality = tq.TimeQuality.from_bytes(b"\x87")
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == tq.DEFAULT_ACCURACY
        assert int(time_quality) == 0x87
        assert bytes(time_quality) == b"\x87"

    # t t t
    def test_true_true_true(self: "TestFromBytes") -> None:
        # 0b1110_0000
        time_quality = tq.TimeQuality.from_bytes(b"\xE0")
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xE0
        assert bytes(time_quality) == b"\xE0"

    # t t f
    def test_true_true_false(self: "TestFromBytes") -> None:
        # 0b1100_0000
        time_quality = tq.TimeQuality.from_bytes(b"\xC0")
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xC0
        assert bytes(time_quality) == b"\xC0"

    # t f t
    def test_true_false_true(self: "TestFromBytes") -> None:
        # 0b1010_0000
        time_quality = tq.TimeQuality.from_bytes(b"\xA0")
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0xA0
        assert bytes(time_quality) == b"\xA0"

    # t f f
    def test_true_false_false(self: "TestFromBytes") -> None:
        # 0b1000_0000
        time_quality = tq.TimeQuality.from_bytes(b"\x80")
        assert time_quality.leap_second_known is True
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x80
        assert bytes(time_quality) == b"\x80"

    # f t t
    def test_false_true_true(self: "TestFromBytes") -> None:
        # 0b0110_0000
        time_quality = tq.TimeQuality.from_bytes(b"\x60")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x60
        assert bytes(time_quality) == b"\x60"

    # f t f
    def test_false_true_false(self: "TestFromBytes") -> None:
        # 0b0100_0000
        time_quality = tq.TimeQuality.from_bytes(b"\x40")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is True
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x40
        assert bytes(time_quality) == b"\x40"

    # f f t
    def test_false_false_true(self: "TestFromBytes") -> None:
        # 0b0010_0000
        time_quality = tq.TimeQuality.from_bytes(b"\x20")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is True
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x20
        assert bytes(time_quality) == b"\x20"

    # f f f
    def test_false_false_false(self: "TestFromBytes") -> None:
        # 0b0000_0000
        time_quality = tq.TimeQuality.from_bytes(b"\x00")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 0
        assert int(time_quality) == 0x00
        assert bytes(time_quality) == b"\x00"

    def test_unspecified_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1111
        time_quality = tq.TimeQuality.from_bytes(b"\x1F")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == tq.UNSPECIFIED_ACCURACY
        assert int(time_quality) == 0x1F
        assert bytes(time_quality) == b"\x1F"

    def test_min_accuracy(self: "TestFromBytes") -> None:
        # 0b0000_0001
        time_quality = tq.TimeQuality.from_bytes(b"\x01")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 1
        assert int(time_quality) == 0x01
        assert bytes(time_quality) == b"\x01"

    def test_max_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1000
        time_quality = tq.TimeQuality.from_bytes(b"\x18")
        assert time_quality.leap_second_known is False
        assert time_quality.clock_failure is False
        assert time_quality.clock_not_sync is False
        assert time_quality.accuracy == 24
        assert int(time_quality) == 0x18
        assert bytes(time_quality) == b"\x18"

    def test_min_invalid_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1001
        with pytest.raises(tq.InvalidAccuracyError) as exc_info:
            tq.TimeQuality.from_bytes(b"\x19")
        exc_info.match("25")

    def test_max_invalid_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1110
        with pytest.raises(tq.InvalidAccuracyError) as exc_info:
            tq.TimeQuality.from_bytes(b"\x1E")
        exc_info.match("30")

