from contextlib import suppress
from socket import AF_PACKET, SOCK_RAW, socket
from sys import argv
from time import time_ns

from pygoose.goose import generate_goose
from pygoose.utils import usleep


def run(interface: str, sleep_until: int) -> None:
    """sleeps until sleep_until, then sends the goose."""
    with socket(AF_PACKET, SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))

        # convert 'ns delta' to 'us delta', then sleeps
        usleep((sleep_until - time_ns()) * 1e-3)

        for wait_for, goose in generate_goose(12):
            usleep(wait_for)
            nic.sendall(goose)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        run(argv[1], int(argv[2]))
