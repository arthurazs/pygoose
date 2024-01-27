from pygoose import utils as u


class TestU32Bytes:
    def test_min(self: "TestU32Bytes") -> None:
        assert u.u32_bytes(0) == b"\x00\x00"

    def test_max(self: "TestU32Bytes") -> None:
        assert u.u32_bytes(0xffff) == b"\xFF\xFF"


class TestMac2Bytes:
    def test_colon(self: "TestMac2Bytes") -> None:
        assert u.mac2bytes("00:00:00:00:00:00") == b"\x00\x00\x00\x00\x00\x00"

    def test_hyphen(self: "TestMac2Bytes") -> None:
        assert u.mac2bytes("00-00-00-00-00-00") == b"\x00\x00\x00\x00\x00\x00"

    def test_neither(self: "TestMac2Bytes") -> None:
        assert u.mac2bytes("000000000000") == b"\x00\x00\x00\x00\x00\x00"

    def test_max(self: "TestMac2Bytes") -> None:
        assert u.mac2bytes("FFFFFFFFFFFF") == b"\xFF\xFF\xFF\xFF\xFF\xFF"


class TestBytes2Mac:
    def test_colon(self: "TestBytes2Mac") -> None:
        assert u.bytes2mac(b"\x00\x00\x00\x00\x00\x00") == "00:00:00:00:00:00"

    def test_hyphen(self: "TestBytes2Mac") -> None:
        assert u.bytes2mac(b"\x00\x00\x00\x00\x00\x00") == "00:00:00:00:00:00"

    def test_neither(self: "TestBytes2Mac") -> None:
        assert u.bytes2mac(b"\x00\x00\x00\x00\x00\x00") == "00:00:00:00:00:00"

    def test_max(self: "TestBytes2Mac") -> None:
        assert u.bytes2mac(b"\xFF\xFF\xFF\xFF\xFF\xFF") == "FF:FF:FF:FF:FF:FF"
