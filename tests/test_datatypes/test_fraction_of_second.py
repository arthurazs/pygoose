import decimal as dec
import pytest

import pygoose.datatypes.time_stamp as ts


class Test:

    def test_000000000000000000000000(self: "Test") -> None:
        expected = dec.Decimal(0)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b000000000000000000000000
        assert bytes(fos) == b"\x00\x00\x00"
        assert fos.value == expected

    def test_000000000000000000000001(self: "Test") -> None:
        expected = dec.Decimal(0.000000059604644775390625)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b000000000000000000000001
        assert bytes(fos) == b"\x00\x00\x01"
        assert fos.value == expected

    def test_000011110001001000000101(self: "Test") -> None:
        expected = dec.Decimal(0.058868706226348876953125)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b000011110001001000000101
        assert bytes(fos) == b"\x0F\x12\x05"
        assert fos.value == expected

    def test_000111100010010000001011(self: "Test") -> None:
        expected = dec.Decimal(0.117737472057342529296875)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b000111100010010000001011
        assert bytes(fos) == b"\x1E\x24\x0B"
        assert fos.value == expected

    def test_001011010011011000010001(self: "Test") -> None:
        expected = dec.Decimal(0.176606237888336181640625)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b001011010011011000010001
        assert bytes(fos) == b"\x2D\x36\x11"
        assert fos.value == expected

    def test_001111000100100000010111(self: "Test") -> None:
        expected = dec.Decimal(0.235475003719329833984375)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b001111000100100000010111
        assert bytes(fos) == b"\x3C\x48\x17"
        assert fos.value == expected

    def test_010010110101101000011101(self: "Test") -> None:
        expected = dec.Decimal(0.294343769550323486328125)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b010010110101101000011101
        assert bytes(fos) == b"\x4B\x5A\x1D"
        assert fos.value == expected

    def test_010110100110110000100011(self: "Test") -> None:
        expected = dec.Decimal(0.353212535381317138671875)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b010110100110110000100011
        assert bytes(fos) == b"\x5A\x6C\x23"
        assert fos.value == expected

    def test_011010010111111000101001(self: "Test") -> None:
        expected = dec.Decimal(0.412081301212310791015625)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b011010010111111000101001
        assert bytes(fos) == b"\x69\x7E\x29"
        assert fos.value == expected

    def test_011110001001000000101111(self: "Test") -> None:
        expected = dec.Decimal(0.470950067043304443359375)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b011110001001000000101111
        assert bytes(fos) == b"\x78\x90\x2F"
        assert fos.value == expected

    def test_100000000000000000000000(self: "Test") -> None:
        expected = dec.Decimal(0.5)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b100000000000000000000000
        assert bytes(fos) == b"\x80\x00\x00"
        assert fos.value == expected

    def test_111111111111111111111111(self: "Test") -> None:
        expected = dec.Decimal(0.999999940395355224609375)
        fos = ts.FractionOfSeconds(expected)
        assert int(fos) == 0b111111111111111111111111
        assert bytes(fos) == b"\xFF\xFF\xFF"
        assert fos.value == expected

    def test_raises_too_big(self: "Test") -> None:
        with pytest.raises(ts.FractionBadSizeError) as exc_info:
            ts.FractionOfSeconds(dec.Decimal(1))
        exc_info.match("too big")

    def test_raises_negative(self: "Test") -> None:
        with pytest.raises(ts.FractionBadSizeError) as exc_info:
            ts.FractionOfSeconds(dec.Decimal(-.1))
        exc_info.match("negative")


class TestFromBytes:

    def test_000000000000000000000000(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0)
        fos = ts.FractionOfSeconds.from_bytes(b"\x00\x00\x00")
        assert int(fos) == 0b000000000000000000000000
        assert bytes(fos) == b"\x00\x00\x00"
        assert fos.value == expected

    def test_000000000000000000000001(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.000000059604644775390625)
        fos = ts.FractionOfSeconds.from_bytes(b"\x00\x00\x01")
        assert int(fos) == 0b000000000000000000000001
        assert bytes(fos) == b"\x00\x00\x01"
        assert fos.value == expected

    def test_000011110001001000000101(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.058868706226348876953125)
        fos = ts.FractionOfSeconds.from_bytes(b"\x0F\x12\x05")
        assert int(fos) == 0b000011110001001000000101
        assert bytes(fos) == b"\x0F\x12\x05"
        assert fos.value == expected

    def test_000111100010010000001011(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.117737472057342529296875)
        fos = ts.FractionOfSeconds.from_bytes(b"\x1E\x24\x0B")
        assert int(fos) == 0b000111100010010000001011
        assert bytes(fos) == b"\x1E\x24\x0B"
        assert fos.value == expected

    def test_001011010011011000010001(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.176606237888336181640625)
        fos = ts.FractionOfSeconds.from_bytes(b"\x2D\x36\x11")
        assert int(fos) == 0b001011010011011000010001
        assert bytes(fos) == b"\x2D\x36\x11"
        assert fos.value == expected

    def test_001111000100100000010111(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.235475003719329833984375)
        fos = ts.FractionOfSeconds.from_bytes(b"\x3C\x48\x17")
        assert int(fos) == 0b001111000100100000010111
        assert bytes(fos) == b"\x3C\x48\x17"
        assert fos.value == expected

    def test_010010110101101000011101(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.294343769550323486328125)
        fos = ts.FractionOfSeconds.from_bytes(b"\x4B\x5A\x1D")
        assert int(fos) == 0b010010110101101000011101
        assert bytes(fos) == b"\x4B\x5A\x1D"
        assert fos.value == expected

    def test_010110100110110000100011(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.353212535381317138671875)
        fos = ts.FractionOfSeconds.from_bytes(b"\x5A\x6C\x23")
        assert int(fos) == 0b010110100110110000100011
        assert bytes(fos) == b"\x5A\x6C\x23"
        assert fos.value == expected

    def test_011010010111111000101001(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.412081301212310791015625)
        fos = ts.FractionOfSeconds.from_bytes(b"\x69\x7E\x29")
        assert int(fos) == 0b011010010111111000101001
        assert bytes(fos) == b"\x69\x7E\x29"
        assert fos.value == expected

    def test_011110001001000000101111(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.470950067043304443359375)
        fos = ts.FractionOfSeconds.from_bytes(b"\x78\x90\x2F")
        assert int(fos) == 0b011110001001000000101111
        assert bytes(fos) == b"\x78\x90\x2F"
        assert fos.value == expected

    def test_100000000000000000000000(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.5)
        fos = ts.FractionOfSeconds.from_bytes(b"\x80\x00\x00")
        assert int(fos) == 0b100000000000000000000000
        assert bytes(fos) == b"\x80\x00\x00"
        assert fos.value == expected

    def test_111111111111111111111111(self: "TestFromBytes") -> None:
        expected = dec.Decimal(0.999999940395355224609375)
        fos = ts.FractionOfSeconds.from_bytes(b"\xFF\xFF\xFF")
        assert int(fos) == 0b111111111111111111111111
        assert bytes(fos) == b"\xFF\xFF\xFF"
        assert fos.value == expected

