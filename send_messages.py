import asyncio
import logging

import aioconsole

from chat_api import authorise, connect_to_chat, submit_message

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    token = await authorise(stream_reader, stream_writer)

    if token is None:
        await aioconsole.aprint('Unknown token. Check it or re-register it.')
        return

    await submit_message(stream_writer, 'message\n')


if __name__ == '__main__':
    asyncio.run(main())
