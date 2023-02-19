import asyncio
import os
from pathlib import Path

import aioconsole

from chat_api import register
from arg_parsers import create_registration_parser
from context_managers import connection_manager
from utils import write_file


async def main() -> None:
    parser = create_registration_parser()
    args = parser.parse_args()
    chat_host, chat_port = args.host, args.port

    async with connection_manager(chat_host, chat_port) as streams:
        stream_reader, stream_writer = streams

        registered_user_data = await register(stream_reader, stream_writer)

        token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
        await write_file(registered_user_data['account_hash'], token_filepath)

        successful_message = (
            'You have successfully registered!\n'
            f'Your nickname: {registered_user_data["nickname"]}\n'
            f'Your token: {registered_user_data["account_hash"]}\n'
            f'Your token is successfully written to the {token_filepath} file'
        )
        await aioconsole.aprint(successful_message)


if __name__ == '__main__':
    asyncio.run(main())
