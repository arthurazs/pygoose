from asyncio import gather
from contextlib import suppress
from socket import AF_PACKET, SOCK_RAW, socket
from sys import argv
from time import time_ns
from typing import TYPE_CHECKING

from uvloop import new_event_loop

from pygoose.goose import generate_goose
from pygoose.utils import async_usleep

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


async def run(loop: "AbstractEventLoop", interface: str, sleep_until: int) -> None:
    """sleeps until sleep_until, then sends the goose."""
    with socket(AF_PACKET, SOCK_RAW, 0xB888) as nic:
        nic.bind((interface, 0))
        nic.setblocking(False)

        # convert 'ns delta' to 'us delta', then sleeps
        await async_usleep((sleep_until - time_ns()) * 1e-3)

        # TODO loop.run_in_executor  para calcular proximo quadro?
        for wait_for, goose in generate_goose(12):
            await gather(async_usleep(wait_for), loop.sock_sendall(nic, goose))


if __name__ == "__main__":
    main_loop = new_event_loop()
    with suppress(KeyboardInterrupt):
        main_loop.run_until_complete(run(main_loop, argv[1], int(argv[2])))
    main_loop.close()
