from pygoose.data_types import (
    bytes2mac,
    bytes2ether,
    bytes2string,
    bytes2u16,
    Timestamp,
)
from pygoose.asn1 import Triplet
import asyncio
import socket
from contextlib import suppress
from itertools import count
from typing import TYPE_CHECKING
from sys import argv


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


async def run(loop: "AbstractEventLoop", interface: str) -> None:
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))
        nic.setblocking(False)

        for counter in count(1):
            elapsed = loop.time()
            data = await loop.sock_recv(nic, 1518)
            mac_dest = bytes2mac(data[0:6])
            mac_src = bytes2mac(data[6:12])
            ether = bytes2ether(data[12:14])
            app_id = bytes2string(data[14:16])

            goose_length = bytes2u16(data[16:18])

            if goose_length != len(data[14:]):
                raise ValueError("GOOSE data missing...")

            reserved1 = bytes2string(data[18:20])
            reserved2 = bytes2string(data[20:22])

            if data[22:23] != b"\x61":
                raise ValueError("Can't find GOOSE PDU")

            pdu = Triplet.unpack(data[22:])

            if pdu.value[0:1] != b"\x80":
                raise ValueError("Can't find GOOSE Control Block Reference")

            t_gocb_ref, padding = Triplet.constructed_unpack(pdu)
            t_ttl, padding = Triplet.constructed_unpack(pdu, padding)
            t_data_set, padding = Triplet.constructed_unpack(pdu, padding)
            t_go_id, padding = Triplet.constructed_unpack(pdu, padding)

            t_timestamp, padding = Triplet.constructed_unpack(pdu, padding)
            timestamp = Timestamp.unpack(t_timestamp.value)

            t_st_num, padding = Triplet.constructed_unpack(pdu, padding)
            t_sq_num, padding = Triplet.constructed_unpack(pdu, padding)
            t_test, padding = Triplet.constructed_unpack(pdu, padding)
            t_conf_rev, padding = Triplet.constructed_unpack(pdu, padding)
            t_nds_com, padding = Triplet.constructed_unpack(pdu, padding)
            t_num_datset_entries, padding = Triplet.constructed_unpack(pdu, padding)

            t_all_data, _ = Triplet.constructed_unpack(pdu, padding)
            t_trip, _ = Triplet.constructed_unpack(t_all_data)

            elapsed = (loop.time() - elapsed) * 1_000
            print(f"{counter} | {elapsed:.3f} ms")
            print(f"{counter} | From {mac_src} to {mac_dest} [{ether}]")
            print(f"{counter} | APPID {app_id}, {goose_length} bytes")
            if "0x0000" not in (reserved1, reserved2):
                print(f"{counter} | Reserved {reserved1}, {reserved2}")
            print()
            print("Control Block Reference:", t_gocb_ref.value.decode("utf8"))
            print("Timeallowed to Tive:", bytes2u16(t_ttl.value))
            print("Data Set:", t_data_set.value.decode("utf8"))
            print("GOOSE ID:", t_go_id.value.decode("utf8"))
            print(f"Timestamp [{timestamp.time_quality}]:\n{timestamp.datetime()}")
            print("Status Number:", int.from_bytes(t_st_num.value, "big"))
            print("Sequence Number:", int.from_bytes(t_sq_num.value, "big"))
            print("Testing:", t_test.value != b"\x00")
            print("Configuration Revision:", int.from_bytes(t_conf_rev.value, "big"))
            print("Needs Commissioning:", t_nds_com.value != b"\x00")
            print(
                "Number of entries:", int.from_bytes(t_num_datset_entries.value, "big")
            )
            print(f"All Data:", t_trip.value != b"\x00")
            print("-" * 10)


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    with suppress(KeyboardInterrupt):
        main_loop.run_until_complete(run(main_loop, argv[1]))
    main_loop.close()
