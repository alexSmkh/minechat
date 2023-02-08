import asyncio
import json
import os
from pathlib import Path
import sys

import aioconsole

from utils import read_file


async def submit_message(stream_writer, message: str, special_chars: str = '') -> None:
    stream_writer.write(message.strip().encode() + b'\n' + special_chars.encode())
    await stream_writer.drain()


async def authorise(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
) -> bool:
    await stream_reader.readline()

    token_filepath = os.path.join(Path(__file__).parent.resolve(), '.token')
    if not os.path.isfile(token_filepath):
        return False

    token = await read_file(token_filepath)
    await submit_message(stream_writer, token)

    auth_result = await stream_reader.readline()

    return not not json.loads(auth_result)


async def register(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
) -> dict:
    await stream_reader.readline()

    await submit_message(stream_writer, '')

    offer_to_enter_nickname = await stream_reader.readline()
    nickname = await aioconsole.ainput(offer_to_enter_nickname.decode())
    await submit_message(stream_writer, f'{nickname}')

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
