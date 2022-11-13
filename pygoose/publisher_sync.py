from contextlib import suppress
from socket import AF_PACKET, SOCK_RAW, socket
from sys import argv

from pygoose.goose import generate_goose
from pygoose.utils import usleep


def run(interface: str) -> None:
    with socket(AF_PACKET, SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))

        # TODO loop.run_in_executor  para calcular proximo quadro?
        for wait_for, goose in generate_goose(12):
            nic.sendall(goose)
            usleep(wait_for)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        run(argv[1])
