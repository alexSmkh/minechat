import asyncio
import json
import logging

from chat_api import connect_to_chat

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    message = await stream_reader.readline()
    logger.debug(message.decode())

    stream_writer.write(b'0d46d7b6-a773-11ed-ad76-0242ac11000' + b'\n')
    await stream_writer.drain()

    message = await stream_reader.readline()
    if json.loads(message) is None:
        print('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return

    logger.debug(message.decode())

    stream_writer.write(b'messsage' + b'\n\n')
    await stream_writer.drain()


if __name__ == '__main__':
    asyncio.run(main())
