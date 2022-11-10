import asyncio
import socket
from contextlib import suppress
from itertools import count
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


async def run(loop: "AbstractEventLoop") -> None:
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0xB888) as nic:
        nic.bind(("lo", 0))
        nic.setblocking(False)

        for counter in count(1):
            elapsed = loop.time()
            data = await loop.sock_recv(nic, 1518)
            print(
                f"{counter}: {(loop.time() - elapsed) * 1_000:.3f} ms | {data[:20]!r}"
            )


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    with suppress(KeyboardInterrupt):
        main_loop.run_until_complete(run(main_loop))
    main_loop.close()
