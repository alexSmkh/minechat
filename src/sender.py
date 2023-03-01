import asyncio
import sys

import aioconsole

from arg_parsers import create_sender_parser
from chat_api import authorise, submit_message
from context_managers import connection_manager
from exceptions import InvalidTokenError, TokenDoesNotExistError
from utils import read_token


async def run_sender(host: str, port: str, token: str, message: str | None) -> None:
    async with connection_manager(host, port) as streams:
        _, stream_writer = streams

        await submit_message(stream_writer, token, '\n')

        if message is not None:
            await submit_message(stream_writer, message, '\n')
            return

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
