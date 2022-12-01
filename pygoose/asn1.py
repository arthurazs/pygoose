from enum import IntEnum
from struct import pack as s_pack
from struct import unpack as s_unpack
from typing import NamedTuple


class IdentifierClass(IntEnum):
    universal = 0
    application = 1
    context = 2
    private = 3


class IdentifierPC(IntEnum):
    primitive = 0
    constructed = 1


class IdentifierType(IntEnum):
    end_of_content = 0
    boolean = 1
    integer = 2
    bit_string = 3
    octet_string = 4
    null = 5
    object_identifier = 6
    object_descriptor = 7
    external = 8
    real = 9
    enumerated = 10
    embedded_pdv = 11
    utf8_string = 12
    relative_oid = 13
    time = 14
    reserved = 15
    sequence_of = 16
    set_of = 17
    numeric_string = 18
    printable_string = 19
    t61string = 20
    videotex_string = 21
    ia5string = 22
    utc_time = 23
    generalized_time = 24
    graphic_string = 25
    visible_string = 26
    general_string = 27
    universal_string = 28
    character_string = 29
    bmp_string = 30
    date = string = 31
    time_of_day = 32
    date_time = 33
    duration = 34
    oid_iri = 35
    relative_oid_iri = 36


class Identifier(NamedTuple):
    id_class: IdentifierClass
    id_pc: IdentifierPC
    id_type: IdentifierType

    def __bytes__(self: "Identifier") -> bytes:
        return s_pack("!B", self.to_int())

    def to_int(self: "Identifier") -> int:
        return (self.id_class << 6) + (self.id_pc << 5) + self.id_type

    @classmethod
    def from_int(cls: type["Identifier"], identifier: int) -> "Identifier":
        id_class = IdentifierClass(identifier >> 6)  # 0b1100_0000
        id_pc = IdentifierPC(identifier >> 5 & 0b1)  # 0b0010_0000
        id_type = IdentifierType(identifier & 0x1F)  # 0b0001_1111
        return cls(id_class=id_class, id_pc=id_pc, id_type=id_type)

    @classmethod
    def unpack(cls: type["Identifier"], identifier: bytes) -> "Identifier":
        i_identifier = s_unpack("!B", identifier)[0]
        return cls.from_int(i_identifier)

    def __str__(self: "Identifier") -> str:
        id_class = self.id_class.name.capitalize()
        id_pc = self.id_pc.name.capitalize()
        if self.id_class.value == 1:
            id_type = f"Application {self.id_type.value}"
        elif self.id_class.value == 2:
            id_type = f"Position {self.id_type.value}"
        else:
            id_type = self.id_type.name.capitalize()
        return f"{hex(self.to_int())} [{id_class}, {id_pc}, {id_type}]"


class Triplet:
    def __init__(self: "Triplet", identifier: int, value: bytes) -> None:
        self.identifier = Identifier.from_int(identifier)
        self.length = len(value)
        if self.length < 0x80:
            self.extra_length = 0
        elif 0x80 <= self.length <= 0xFF:
            self.extra_length = 1
        elif 0xFF < self.length <= 0xFFFF:
            self.extra_length = 2
        elif 0xFFFF < self.length <= 0xFFFFFF:
            self.extra_length = 3
        else:
            raise ValueError("Value too big")
        self.value = value

    def __len__(self: "Triplet") -> int:
        return self.length + self.extra_length + 2

    def __bytes__(self: "Triplet") -> bytes:
        if self.length < 0x80:
            return bytes(self.identifier) + s_pack("!B", self.length) + self.value
        elif self.length <= 0xFF:
            return (
                bytes(self.identifier) + s_pack("!BB", 0x81, self.length) + self.value
            )
        elif self.length <= 0xFFFF:
            return (
                bytes(self.identifier) + s_pack("!BH", 0x82, self.length) + self.value
            )
        elif self.length <= 0xFFFFFF:
            return (
                bytes(self.identifier)
                + s_pack("!B", 0x83)
                + s_pack("!I", self.length)[1:]
                + self.value
            )
        raise ValueError("Value too big")

    @classmethod
    def constructed_unpack(
        cls: type["Triplet"], triplet: "Triplet", padding: int = 0
    ) -> tuple["Triplet", int]:
        new_triplet = cls.unpack(triplet.value[padding:])
        return new_triplet, padding + len(new_triplet)

    @classmethod
    def unpack(cls: type["Triplet"], bytes_string: bytes) -> "Triplet":
        identifier = Identifier.unpack(bytes_string[0:1])
        length = s_unpack("!B", bytes_string[1:2])[0]

        index = 0
        if length == 0x80:
            length = s_unpack("!B", bytes_string[2:3])[0]
            index = 1
        elif length == 0x81:
            length = s_unpack("!H", bytes_string[2:4])[0]
            index = 2
        elif length == 0x82:
            length = s_unpack("!I", b"\x00" + bytes_string[2:5])[0]
            index = 3
        elif length >= 0x83:
            raise ValueError("Value too big")

        value = bytes_string[2 + index :]

        if length > len(value):
            raise ValueError("Triplet missing data")

        return cls(identifier=identifier.to_int(), value=value[:length])

    def __str__(self: "Triplet") -> str:
        return f"{self.identifier} [{self.length} bytes]:\n{self.value!r}"
