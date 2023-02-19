import asyncio
import logging
import os
from pathlib import Path

import aioconsole

from chat_api import authorise, submit_message
from arg_parsers import create_sender_parser
from context_managers import connection_manager
from utils import read_file


async def main() -> None:
    parser = create_sender_parser()
    args = parser.parse_args()
    chat_host, chat_port = args.host, args.port

    async with connection_manager(chat_host, chat_port) as streams:
        stream_reader, stream_writer = streams

        token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
        if not os.path.isfile(token_filepath):
            await aioconsole.aprint('You do not have a token. Please register')
            return

        token = await read_file(token_filepath)

        auth_result = await authorise(stream_reader, stream_writer, token)
        if not auth_result:
            await aioconsole.aprint('Unknown token. Check it or re-register it.')
            return

        if args.__dict__.get('interactive'):
            while True:
                message = await aioconsole.ainput('> ')
                await submit_message(stream_writer, message, '\n')
        elif message := args.__dict__.get('message'):
            await submit_message(stream_writer, message, '\n')
        else:
            await aioconsole.ainput('You need to specify a message or enable interactive mode.')


if __name__ == '__main__':
    asyncio.run(main())
