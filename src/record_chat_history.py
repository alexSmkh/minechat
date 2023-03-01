import asyncio
import logging
from datetime import datetime

from arg_parsers import create_record_history_parser
from chat_api import read_chat
from context_managers import connection_manager
from utils import write_file

logger = logging.getLogger(__file__)


async def save_message(message: str, history_filepath: str, log: bool = False) -> None:
    if log:
        logger.debug(message)

    time = datetime.now().strftime('%d.%m.%y %H:%M:%S')
    await write_file(f'[{time}] {message}', history_filepath, mode='a')


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    parser = create_record_history_parser()
    args = parser.parse_args()
    chat_host, chat_port, history_filepath = args.host, args.port, args.history

    async with connection_manager(chat_host, chat_port) as streams:
        stream_reader, stream_writer = streams
        async for message in read_chat(stream_reader, stream_writer):
            await save_message(message, history_filepath, log=True)


if __name__ == '__main__':
    asyncio.run(main())
