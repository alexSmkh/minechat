import asyncio
import aioconsole
import json
import logging

from chat_api import connect_to_chat, register

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    registered_user_data = await register(stream_reader, stream_writer)

    success_message = (
        'You have successfully registered!\n'
        f'Your nickname: {registered_user_data["nickname"]}\n'
        f'Your token: {registered_user_data["account_hash"]}\n'
    )
    await aioconsole.aprint(success_message)


if __name__ == '__main__':
    asyncio.run(main())
