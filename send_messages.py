import asyncio
from chat_api import connect_to_chat


async def main() -> None:
    chat_host = 'minechat.dvmn.org'
    chat_port = '5050'
    _, stream_writer = await connect_to_chat(chat_host, chat_port)

    stream_writer.write(b'0d46d7b6-a773-11ed-ad76-0242ac110002' + b'\n')
    await stream_writer.drain()

    stream_writer.write(b'messsage' + b'\n\n')
    await stream_writer.drain()


if __name__ == '__main__':
    asyncio.run(main())
