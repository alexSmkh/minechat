import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import configargparse

from chat_api import connect_to_chat, read_chat
from utils import write_file

logger = logging.getLogger(__file__)


async def record_chat_history(stream_reader: asyncio.StreamReader, history_filepath) -> None:
    async for message in read_chat(stream_reader):
        time = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        logger.debug(message)
        await write_file(f'[{time}] {message}', history_filepath, mode='a')


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
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    parser = create_parser()
    args = parser.parse_args()
    chat_host, chat_port, history_filepath = args.host, args.port, args.history

    stream_reader, _ = await connect_to_chat(chat_host, chat_port)

    await asyncio.gather(
        record_chat_history(stream_reader, history_filepath),
    )


if __name__ == '__main__':
    asyncio.run(main())
