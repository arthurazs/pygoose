import pytest

import pygoose.datatypes as dt


class TestLeapFailureSync:
    def test_default(self: "TestLeapFailureSync") -> None:
        # 0b1000_0111
        tq = dt.TimeQuality.default()
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == dt.DEFAULT_ACCURACY
        assert bytes(tq) == b"\x87"

    # t t t
    def test_true_true_true(self: "TestLeapFailureSync") -> None:
        # 0b1110_0000
        tq = dt.TimeQuality(leap_second_known=True, clock_failure=True, clock_not_sync=True, accuracy=0)
        assert tq.leap_second_known is True
        assert tq.clock_failure is True
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xE0"

    # t t f
    def test_true_true_false(self: "TestLeapFailureSync") -> None:
        # 0b1100_0000
        tq = dt.TimeQuality(leap_second_known=True, clock_failure=True, clock_not_sync=False, accuracy=0)
        assert tq.leap_second_known is True
        assert tq.clock_failure is True
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xC0"

    # t f t
    def test_true_false_true(self: "TestLeapFailureSync") -> None:
        # 0b1010_0000
        tq = dt.TimeQuality(leap_second_known=True, clock_failure=False, clock_not_sync=True, accuracy=0)
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xA0"

    # t f f
    def test_true_false_false(self: "TestLeapFailureSync") -> None:
        # 0b1000_0000
        tq = dt.TimeQuality(leap_second_known=True, clock_failure=False, clock_not_sync=False, accuracy=0)
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x80"

    # f t t
    def test_false_true_true(self: "TestLeapFailureSync") -> None:
        # 0b0110_0000
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=True, clock_not_sync=True, accuracy=0)
        assert tq.leap_second_known is False
        assert tq.clock_failure is True
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x60"

    # f t f
    def test_false_true_false(self: "TestLeapFailureSync") -> None:
        # 0b0100_0000
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=True, clock_not_sync=False, accuracy=0)
        assert tq.leap_second_known is False
        assert tq.clock_failure is True
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x40"

    # f f t
    def test_false_false_true(self: "TestLeapFailureSync") -> None:
        # 0b0010_0000
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=True, accuracy=0)
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x20"

    # f f f
    def test_false_false_false(self: "TestLeapFailureSync") -> None:
        # 0b0000_0000
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=0)
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x00"


class TestAccuracy:
    def test_unspecified_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1111
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False,
                            accuracy=dt.UNSPECIFIED_ACCURACY)
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == dt.UNSPECIFIED_ACCURACY
        assert bytes(tq) == b"\x1F"

    def test_min_accuracy(self: "TestAccuracy") -> None:
        # 0b0000_0001
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=1)
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 1
        assert bytes(tq) == b"\x01"

    def test_max_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1000
        tq = dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=24)
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 24
        assert bytes(tq) == b"\x18"

    def test_min_invalid_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1001
        with pytest.raises(dt.InvalidAccuracyError) as exc_info:
            dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=25)
        assert exc_info.match("25")

    def test_max_invalid_accuracy(self: "TestAccuracy") -> None:
        # 0b0001_1110
        with pytest.raises(ValueError) as exc_info:
            dt.TimeQuality(leap_second_known=False, clock_failure=False, clock_not_sync=False, accuracy=30)
        assert exc_info.match("30")


class TestFromBytes:
    def test_default(self: "TestFromBytes") -> None:
        # 0b1000_0111
        tq = dt.TimeQuality.from_bytes(b"\x87")
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == dt.DEFAULT_ACCURACY
        assert bytes(tq) == b"\x87"

    # t t t
    def test_true_true_true(self: "TestFromBytes") -> None:
        # 0b1110_0000
        tq = dt.TimeQuality.from_bytes(b"\xE0")
        assert tq.leap_second_known is True
        assert tq.clock_failure is True
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xE0"

    # t t f
    def test_true_true_false(self: "TestFromBytes") -> None:
        # 0b1100_0000
        tq = dt.TimeQuality.from_bytes(b"\xC0")
        assert tq.leap_second_known is True
        assert tq.clock_failure is True
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xC0"

    # t f t
    def test_true_false_true(self: "TestFromBytes") -> None:
        # 0b1010_0000
        tq = dt.TimeQuality.from_bytes(b"\xA0")
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\xA0"

    # t f f
    def test_true_false_false(self: "TestFromBytes") -> None:
        # 0b1000_0000
        tq = dt.TimeQuality.from_bytes(b"\x80")
        assert tq.leap_second_known is True
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x80"

    # f t t
    def test_false_true_true(self: "TestFromBytes") -> None:
        # 0b0110_0000
        tq = dt.TimeQuality.from_bytes(b"\x60")
        assert tq.leap_second_known is False
        assert tq.clock_failure is True
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x60"

    # f t f
    def test_false_true_false(self: "TestFromBytes") -> None:
        # 0b0100_0000
        tq = dt.TimeQuality.from_bytes(b"\x40")
        assert tq.leap_second_known is False
        assert tq.clock_failure is True
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x40"

    # f f t
    def test_false_false_true(self: "TestFromBytes") -> None:
        # 0b0010_0000
        tq = dt.TimeQuality.from_bytes(b"\x20")
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is True
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x20"

    # f f f
    def test_false_false_false(self: "TestFromBytes") -> None:
        # 0b0000_0000
        tq = dt.TimeQuality.from_bytes(b"\x00")
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 0
        assert bytes(tq) == b"\x00"

    def test_unspecified_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1111
        tq = dt.TimeQuality.from_bytes(b"\x1F")
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == dt.UNSPECIFIED_ACCURACY
        assert bytes(tq) == b"\x1F"

    def test_min_accuracy(self: "TestFromBytes") -> None:
        # 0b0000_0001
        tq = dt.TimeQuality.from_bytes(b"\x01")
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 1
        assert bytes(tq) == b"\x01"

    def test_max_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1000
        tq = dt.TimeQuality.from_bytes(b"\x18")
        assert tq.leap_second_known is False
        assert tq.clock_failure is False
        assert tq.clock_not_sync is False
        assert tq.accuracy == 24
        assert bytes(tq) == b"\x18"

    def test_min_invalid_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1001
        with pytest.raises(dt.InvalidAccuracyError) as exc_info:
            dt.TimeQuality.from_bytes(b"\x19")
        assert exc_info.match("25")

    def test_max_invalid_accuracy(self: "TestFromBytes") -> None:
        # 0b0001_1110
        with pytest.raises(ValueError) as exc_info:
            dt.TimeQuality.from_bytes(b"\x1E")
        assert exc_info.match("30")

