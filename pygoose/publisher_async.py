import asyncio
import decimal as dec
import socket
from contextlib import suppress
from struct import pack as s_pack
from time import time_ns
from typing import TYPE_CHECKING

from sys import argv

from pygoose.asn1 import Triplet
from pygoose.data_types import TimeQuality, Timestamp, ether2bytes, mac2bytes, u32_bytes

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


def new_datetime(quality: TimeQuality) -> Triplet:
    now = dec.Decimal(time_ns()) * dec.Decimal(1e-9)
    epoch = int(now)
    fraction = int((now % 1) * int(1e9))
    timestamp = Timestamp(
        second_since_epoch=epoch, fraction_of_second=fraction, time_quality=quality
    )
    return Triplet(0x84, bytes(timestamp))


async def run(loop: "AbstractEventLoop", interface: str) -> None:
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

    quality = TimeQuality(
        leap_second_know=True, clock_failure=False, clock_not_sync=False, accuracy=18
    )
    t = new_datetime(quality)

    b_go_id = bytes(Triplet(0x83, b"SEL_421_Sub"))
    b_dat_set = bytes(Triplet(0x82, b"SEL_421_SubCFG/LLN0$PIOC"))
    b_time_allowed_to_live = bytes(Triplet(0x81, u32_bytes(2000)))

    b_gocb_ref = bytes(Triplet(0x80, b"SEL_421_SubCFG/LLN0$GO$PIOC"))

    trip = False
    seq = 1
    status = 1
    sleeping_times = (0, 0.002, 0.004, 0.008, 1)

    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))
        nic.setblocking(False)

        for index in range(10):

            if index == 4:
                trip = True
                t = new_datetime(quality)
                status += 1
                seq = 0

            try:
                wait_for = sleeping_times[seq]
            except IndexError:
                wait_for = 1

            if index == 3:
                wait_for = 0.104749

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
            # TODO loop.run_in_executor  para calcular proximo quadro?
            await asyncio.gather(asyncio.sleep(wait_for), loop.sock_sendall(nic, goose))
            seq += 1


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    with suppress(KeyboardInterrupt):
        main_loop.run_until_complete(run(main_loop, argv[1]))
    main_loop.close()
