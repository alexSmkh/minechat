import asyncio
import sys
from datetime import datetime

import aiofiles


async def write_chat_history(message: str) -> None:
    async with aiofiles.open('chat.txt', mode='a') as file:
        time = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        await file.write(f'[{time}] {message}')


async def connect_to_chat(host: str, port: str) -> None:
    reader, _ = await asyncio.open_connection(host, port)

    max_error_count = 5
    error_counter = 0
    while True:
        try:
            async with asyncio.timeout(5):
                message = await reader.readline()

            decoded_message = message.decode()
            await write_chat_history(decoded_message)
            print(decoded_message)

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


async def main() -> None:
    chat_host = 'minechat.dvmn.org'
    chat_port = '5000'

    await asyncio.gather(
        connect_to_chat(chat_host, chat_port),
    )


if __name__ == '__main__':
    asyncio.run(main())
