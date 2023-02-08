import asyncio
import logging
import os
from pathlib import Path

import aioconsole

from chat_api import connect_to_chat, register
from utils import write_file

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    registered_user_data = await register(stream_reader, stream_writer)

    token_filepath = os.path.join(Path(__file__).parent.resolve(), '.token')
    await write_file(registered_user_data['account_hash'], token_filepath)

    success_message = (
        'You have successfully registered!\n'
        f'Your nickname: {registered_user_data["nickname"]}\n'
        f'Your token: {registered_user_data["account_hash"]}\n'
        f'Your token is successfully written to the .token file'
    )
    await aioconsole.aprint(success_message)


if __name__ == '__main__':
    asyncio.run(main())
