import asyncio
import json
import sys

import aioconsole
from exceptions import InvalidTokenError


async def submit_message(stream_writer, message: str, special_chars: str = '') -> None:
    stream_writer.write(message.strip().encode() + b'\n' + special_chars.encode())
    await stream_writer.drain()


async def authorise(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
    token: str,
) -> None:
    await stream_reader.readline()
    await submit_message(stream_writer, token)

    auth_result = await stream_reader.readline()

    if not json.loads(auth_result):
        raise InvalidTokenError('Token is invalid. Check it or re-register it.')


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


async def read_chat(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
) -> str:
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
                stream_writer.close()
                await stream_writer.wait_closed()
                return

            print(
                'Internet connection problems... Please wait...',
                file=sys.stderr,
            )
            max_error_count += 1
            await asyncio.sleep(5)
