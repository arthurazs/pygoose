from struct import pack as s_pack
from typing import TYPE_CHECKING, NamedTuple

from pygoose.asn1 import Triplet
from pygoose.data_types import (
    Timestamp,
    bytes2ether,
    bytes2hexstring,
    bytes2mac,
    bytes2string,
    bytes2u16,
    ether2bytes,
    mac2bytes,
    u32_bytes,
)
from pygoose.utils import now

if TYPE_CHECKING:
    from typing import Iterator


def generate_goose(index_range: int) -> "Iterator[tuple[float, bytes]]":
    b_dst_addr = mac2bytes("01:0c:cd:01:00:01")
    b_src_addr = mac2bytes("00-30-a7-22-9d-01")
    b_goose_ether = ether2bytes("88b8")
    b_app_id = u32_bytes(0)
    b_reserved = u32_bytes(0) + u32_bytes(0)
    b_header = b_dst_addr + b_src_addr + b_goose_ether + b_app_id

    b_num_dat_set_entries = bytes(Triplet(0x8A, b"\x01"))

    b_nds_com = bytes(Triplet(0x89, b"\x00"))
    b_conf_rev = bytes(Triplet(0x88, b"\x01"))
    b_test = bytes(Triplet(0x87, b"\x00"))

    t = now()

    b_go_id = bytes(Triplet(0x83, b"SEL_421_Sub"))
    b_dat_set = bytes(Triplet(0x82, b"SEL_421_SubCFG/LLN0$PIOC"))
    b_time_allowed_to_live = bytes(Triplet(0x81, u32_bytes(2000)))

    b_gocb_ref = bytes(Triplet(0x80, b"SEL_421_SubCFG/LLN0$GO$PIOC"))

    trip = False
    seq = 1  # noqa
    status = 1
    sleeping_times = (0.0, 2 * 1e3, 4 * 1e3, 8 * 1e3)

    for index in range(index_range):

        try:
            wait_for = sleeping_times[seq - 1 if status == 1 else seq]
        except IndexError:
            wait_for = 1 * 1e6

        if index == 4:
            trip = True
            t = now()
            status += 1
            seq = 0
            # trigger = 104_617
            # time_spent_so_far = 14 * 1e3 = (0 + 2 + 4 + 8) * 1e3
            wait_for = 104_617.0 - (14 * 1e3)
        elif index == 8:
            trip = False
            t = now()
            status += 1
            seq = 0
            # untrigger = 075_441.0
            wait_for = 075_441.0

        # TODO bool 0x0F not defined
        data_bool = Triplet(0x83, b"\x0f" if trip else b"\x00")
        data = Triplet(0xAB, bytes(data_bool))

        sq_num = Triplet(0x86, s_pack("!B", seq))
        st_num = Triplet(0x85, s_pack("!B", status))

        b_goose_pdu = bytes(
            Triplet(
                0x61,
                b_gocb_ref
                + b_time_allowed_to_live
                + b_dat_set
                + b_go_id
                + bytes(t)
                + bytes(st_num)
                + bytes(sq_num)
                + b_test
                + b_conf_rev
                + b_nds_com
                + b_num_dat_set_entries
                + bytes(data),
            )
        )
        b_length = u32_bytes(len(b_goose_pdu) + 8)
        goose = b_header + b_length + b_reserved + b_goose_pdu
        yield wait_for, goose
        seq += 1


class GOOSE(NamedTuple):
    mac_dest: str
    mac_src: str
    ether: str
    app_id: str
    goose_length: int
    reserved1: str
    reserved2: str
    gocb_ref: str
    ttl: int
    data_set: str
    go_id: str
    timestamp: Timestamp
    st_num: int
    sq_num: int
    test: bool
    conf_rev: int
    nds_com: bool
    num_datset_entries: int
    trip: bool


def unpack_goose(bytes_string: bytes) -> GOOSE:
    mac_dest = bytes2mac(bytes_string[0:6])
    mac_src = bytes2mac(bytes_string[6:12])
    ether = bytes2ether(bytes_string[12:14])
    app_id = bytes2hexstring(bytes_string[14:16])

    goose_length = bytes2u16(bytes_string[16:18])

    if goose_length != len(bytes_string[14:]):
        raise ValueError("GOOSE data missing...")

    reserved1 = bytes2hexstring(bytes_string[18:20])
    reserved2 = bytes2hexstring(bytes_string[20:22])

    if bytes_string[22:23] != b"\x61":
        raise ValueError("Can't find GOOSE PDU")

    pdu = Triplet.unpack(bytes_string[22:])

    if pdu.value[0:1] != b"\x80":
        raise ValueError("Can't find GOOSE Control Block Reference")

    t_gocb_ref, padding = Triplet.constructed_unpack(pdu)
    gocb_ref = bytes2string(t_gocb_ref.value)

    t_ttl, padding = Triplet.constructed_unpack(pdu, padding)
    ttl = int.from_bytes(t_ttl.value, "big")  # TODO check size, use pack

    t_data_set, padding = Triplet.constructed_unpack(pdu, padding)
    data_set = bytes2string(t_data_set.value)

    t_go_id, padding = Triplet.constructed_unpack(pdu, padding)
    go_id = bytes2string(t_go_id.value)

    t_timestamp, padding = Triplet.constructed_unpack(pdu, padding)
    timestamp = Timestamp.unpack(t_timestamp.value)

    t_st_num, padding = Triplet.constructed_unpack(pdu, padding)
    st_num = int.from_bytes(t_st_num.value, "big")

    t_sq_num, padding = Triplet.constructed_unpack(pdu, padding)
    sq_num = int.from_bytes(t_sq_num.value, "big")

    t_test, padding = Triplet.constructed_unpack(pdu, padding)
    test = t_test.value != b"\x00"

    t_conf_rev, padding = Triplet.constructed_unpack(pdu, padding)
    conf_rev = int.from_bytes(t_conf_rev.value, "big")

    t_nds_com, padding = Triplet.constructed_unpack(pdu, padding)
    nds_com = t_nds_com.value != b"\x00"

    t_num_datset_entries, padding = Triplet.constructed_unpack(pdu, padding)
    num_datset_entries = int.from_bytes(t_num_datset_entries.value, "big")

    t_all_data, _ = Triplet.constructed_unpack(pdu, padding)
    t_trip, _ = Triplet.constructed_unpack(t_all_data)
    trip = t_trip.value != b"\x00"

    return GOOSE(
        mac_dest=mac_dest,
        mac_src=mac_src,
        ether=ether,
        app_id=app_id,
        goose_length=goose_length,
        reserved1=reserved1,
        reserved2=reserved2,
        gocb_ref=gocb_ref,
        ttl=ttl,
        data_set=data_set,
        go_id=go_id,
        timestamp=timestamp,
        st_num=st_num,
        sq_num=sq_num,
        test=test,
        conf_rev=conf_rev,
        nds_com=nds_com,
        num_datset_entries=num_datset_entries,
        trip=trip,
    )
