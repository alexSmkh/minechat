import asyncio
import logging
import sys
import aioconsole
import json


async def register(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
) -> dict:
    await stream_reader.readline()

    stream_writer.write(b'\n')
    await stream_writer.drain()

    offer_to_enter_nickname = await stream_reader.readline()
    await aioconsole.aprint(offer_to_enter_nickname.decode())

    nickname = await aioconsole.ainput()
    stream_writer.write(nickname.encode() + b'\n')
    await stream_writer.drain()

    return json.loads(await stream_reader.readline())


async def read_chat(stream_reader: asyncio.StreamReader) -> str:
    max_error_count = 5
    error_counter = 0
    while True:
        try:
            async with asyncio.timeout(5):
                message = await stream_reader.readline()

            yield message.decode()

            error_counter = 0
        except TimeoutError:
            if error_counter == max_error_count:
                print(
                    'Internet connection problems. Please try again later',
                    file=sys.stderr,
                )
                break

            print(
                'Internet connection problems... Please wait...',
                file=sys.stderr,
            )
            max_error_count += 1
            await asyncio.sleep(5)


async def connect_to_chat(
    host: str, port: str
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer
