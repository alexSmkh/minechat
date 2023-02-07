import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

import aiofiles
import configargparse


async def write_chat_history(message: str, history_path: str) -> None:
    async with aiofiles.open(history_path, mode='a') as file:
        time = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        await file.write(f'[{time}] {message}')


async def connect_to_chat(host: str, port: str, history_path: str) -> None:
    reader, _ = await asyncio.open_connection(host, port)

    max_error_count = 5
    error_counter = 0
    while True:
        try:
            async with asyncio.timeout(5):
                message = await reader.readline()

            decoded_message = message.decode()
            await write_chat_history(decoded_message, history_path)
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


def create_parser() -> configargparse.ArgParser:
    root_path = Path(__file__).parent.resolve()

    parser = configargparse.ArgParser(
        default_config_files=[os.path.join(root_path, 'config.yml')],
    )
    parser.add('--config', type=str, is_config_file=True, help='Config file path')
    parser.add('--host', type=str, required=True, help='Chat host')
    parser.add('--port', type=str, required=True, help='Chat port')
    parser.add(
        '--history',
        default=os.path.join(root_path, 'minechat.history'),
        help='The path to the correspondence history file. \
            Default value: /path_to_project_root/minechat.history',
    )
    return parser


async def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    chat_host, chat_port, history_path = args.host, args.port, args.history

    await asyncio.gather(
        connect_to_chat(chat_host, chat_port, history_path),
    )


if __name__ == '__main__':
    asyncio.run(main())
