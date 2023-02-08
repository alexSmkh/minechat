import asyncio
import json
import logging
import aioconsole

from chat_api import connect_to_chat, submit_message

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    message = await stream_reader.readline()
    logger.debug(message.decode())

    await submit_message(stream_writer, '0d46d7b6-a773-11ed-ad76-0242ac11000')

    message = await stream_reader.readline()
    if json.loads(message) is None:
        await aioconsole.aprint('Unknown token. Check it or re-register it.')
        return

    logger.debug(message.decode())

    await submit_message(stream_writer, 'message\n')


if __name__ == '__main__':
    asyncio.run(main())
