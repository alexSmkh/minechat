import asyncio
import os
from pathlib import Path

import aioconsole

from arg_parsers import create_sender_parser
from chat_api import authorise, submit_message
from context_managers import connection_manager
from exceptions import InvalidTokenError, TokenDoesNotExistError
from utils import read_file


async def read_token() -> str:
    token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
    if os.path.isfile(token_filepath):
        return await read_file(token_filepath)
    raise TokenDoesNotExistError('You do not have a token. Please register')


async def run_sender(
    stream_writer: asyncio.StreamReader,
    message: str | None,
) -> None:
    if message is not None:
        await submit_message(stream_writer, message, '\n')
        return

    while True:
        message = await aioconsole.ainput('> ')
        await submit_message(stream_writer, message, '\n')


async def main() -> None:
    parser = create_sender_parser()
    args = parser.parse_args()
    chat_host, chat_port = args.host, args.port

    async with connection_manager(chat_host, chat_port) as streams:
        stream_reader, stream_writer = streams

        try:
            token = await read_token()
            await authorise(stream_reader, stream_writer, token)
        except (TokenDoesNotExistError, InvalidTokenError) as err:
            await aioconsole.aprint(err)
            return

        await run_sender(
            stream_writer,
            args.__dict__.get('message'),
        )

if __name__ == '__main__':
    asyncio.run(main())
