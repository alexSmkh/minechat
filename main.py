import asyncio
import sys


async def connect_to_chat(host: str, port: str) -> None:
    reader, _ = await asyncio.open_connection(host, port)

    max_error_count = 5
    error_counter = 0
    while True:
        try:
            async with asyncio.timeout(5):
                messages = await reader.readline()
            print(messages.decode())

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
