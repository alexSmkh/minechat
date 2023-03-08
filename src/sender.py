import asyncio
import sys
from typing import Dict

import aioconsole

from arg_parsers import create_sender_parser
from chat_api import authorise, submit_message
from context_managers import connection_manager
from exceptions import InvalidTokenError, TokenDoesNotExistError
from gui import SendingConnectionStateChanged
from utils import read_token


async def run_sender(
    host: str,
    port: str,
    queues: Dict[str, asyncio.Queue] = {},
    message: str = None,
) -> None:
    status_queue = queues.get('status_updates')
    if status_queue is not None:
        status_queue.put_nowait(SendingConnectionStateChanged.INITIATED)

    async with connection_manager(host, port) as streams:
        _, stream_writer = streams

        token = await read_token()
        await submit_message(stream_writer, token, '\n')

        if message is not None:
            await submit_message(stream_writer, message, '\n')
            return

        sending_queue = queues.get('sending')
        watchdog_queue = queues.get('watchdog')
        if sending_queue is not None:
            status_queue.put_nowait(SendingConnectionStateChanged.ESTABLISHED)
            while True:
                message = await sending_queue.get()
                await submit_message(stream_writer, message, '\n')
                watchdog_queue.put_nowait('Message sent')

        while True:
            message = await aioconsole.ainput('> ')
            await submit_message(stream_writer, message, '\n')


async def main() -> None:
    parser = create_sender_parser()
    args = parser.parse_args()
    host, port = args.host, args.sending_port

    try:
        token = await read_token()
        await authorise(host, port, token)
    except (TokenDoesNotExistError, InvalidTokenError) as err:
        await aioconsole.aprint(err)
        return

    await run_sender(host, port, token, args.__dict__.get('message'))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
