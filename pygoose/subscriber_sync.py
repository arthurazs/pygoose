from contextlib import suppress
from itertools import count
from socket import AF_PACKET, SOCK_RAW, socket
from sys import argv
from time import time_ns

from pygoose.goose import unpack_goose


def run(interface: str) -> None:
    with socket(AF_PACKET, SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))

        for counter in count(1):
            elapsed: float = time_ns()
            data = nic.recv(1518)
            (
                mac_dest,
                mac_src,
                ether,
                app_id,
                goose_length,
                reserved1,
                reserved2,
                gocb_ref,
                ttl,
                data_set,
                go_id,
                timestamp,
                st_num,
                sq_num,
                test,
                conf_rev,
                nds_com,
                num_datset_entries,
                trip,
            ) = unpack_goose(data)

            elapsed = (time_ns() - elapsed) * 1e-6
            print(
                f"{counter} | {elapsed:.3f} ms\n"
                f"{counter} | From {mac_src} to {mac_dest} [{ether}]\n"
                f"{counter} | APPID {app_id}, {goose_length} bytes"
            )
            if "0x0000" not in (reserved1, reserved2):
                print(f"{counter} | Reserved {reserved1}, {reserved2}")
            print(
                f"\nControl Block Reference: {gocb_ref}\n"
                f"Time Allowed to Live: {ttl}\n"
                f"Data Set: {data_set}\n"
                f"GOOSE ID: {go_id}\n"
                # TODO Timestamp is okay?
                f"Timestamp [{timestamp.time_quality}]:\n{timestamp.datetime()}\n"
                f"Status Number: {st_num}\n"
                f"Sequence Number: {sq_num}\n"
                f"Testing: {test}\n"
                f"Configuration Revision: {conf_rev}\n"
                f"Needs Commissioning: {nds_com}\n"
                f"Number of entries: {num_datset_entries}\n"
                f"All Data: {trip}"
            )
            print("-" * 10)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        run(argv[1])
