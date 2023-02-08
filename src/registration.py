import asyncio
import os
from pathlib import Path

import aioconsole

from chat_api import register
from arg_parsers import create_registration_parser
from utils import write_file


async def main() -> None:
    parser = create_registration_parser()
    args = parser.parse_args()
    chat_host, chat_port = args.host, args.port

    stream_reader, stream_writer = await asyncio.open_connection(chat_host, chat_port)

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

    stream_writer.close()
    await stream_writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
