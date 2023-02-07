import asyncio
import sys


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
