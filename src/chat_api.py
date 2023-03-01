import asyncio
import json
import sys

import aioconsole
from context_managers import connection_manager

from exceptions import InvalidTokenError


async def submit_message(stream_writer, message: str, special_chars: str = '') -> None:
    stream_writer.write(message.strip().encode() + b'\n' + special_chars.encode())
    await stream_writer.drain()


async def authorise(host: str, port: str, token: str) -> dict:
    async with connection_manager(host, port) as streams:
        stream_reader, stream_writer = streams

        await stream_reader.readline()
        await submit_message(stream_writer, token)

        auth_result = json.loads(await stream_reader.readline())

        if not auth_result:
            raise InvalidTokenError('Token is invalid. Check it or re-register it.')

        return auth_result

async def register(host: str, port: str) -> dict:
    async with connection_manager(host, port) as streams:
        stream_reader, stream_writer = streams
        await stream_reader.readline()

        await submit_message(stream_writer, '')

        offer_to_enter_nickname = await stream_reader.readline()
        nickname = await aioconsole.ainput(offer_to_enter_nickname.decode())
        await submit_message(stream_writer, f'{nickname}')

        return json.loads(await stream_reader.readline())


async def read_chat(host: str, port: str) -> str:
    async with connection_manager(host, port) as streams:
        stream_reader, _ = streams
        while True:
            message = await stream_reader.readline()
            yield message.decode()
