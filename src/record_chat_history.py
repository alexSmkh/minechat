import asyncio
import logging
from datetime import datetime

from arg_parsers import create_record_history_parser
from chat_api import read_chat
from context_managers import connection_manager
from utils import write_file

logger = logging.getLogger(__file__)


async def record_chat_history(
    stream_reader: asyncio.StreamReader,
    stream_writer: asyncio.StreamWriter,
    history_filepath,
) -> None:
    async for message in read_chat(stream_reader, stream_writer):
        time = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        logger.debug(message)
        await write_file(f'[{time}] {message}', history_filepath, mode='a')


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    parser = create_record_history_parser()
    args = parser.parse_args()
    chat_host, chat_port, history_filepath = args.host, args.port, args.history

    async with connection_manager(chat_host, chat_port) as streams:
        stream_reader, stream_writer = streams
        await asyncio.gather(
            record_chat_history(stream_reader, stream_writer, history_filepath),
        )


if __name__ == '__main__':
    asyncio.run(main())
