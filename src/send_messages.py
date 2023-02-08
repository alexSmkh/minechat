import asyncio
import logging
import os
from pathlib import Path

import aioconsole

from chat_api import authorise, connect_to_chat, submit_message
from arg_parsers import create_sender_parser
from utils import read_file

logger = logging.getLogger(__file__)


async def main() -> None:
    logging.basicConfig(format='%(levelname)s:sender:%(message)s', level=logging.DEBUG)

    parser = create_sender_parser()
    args = parser.parse_args()
    chat_host, chat_port, message = args.host, args.port, args.message

    stream_reader, stream_writer = await connect_to_chat(chat_host, chat_port)

    token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
    if not os.path.isfile(token_filepath):
        await aioconsole.aprint('You do not have a token. Please register')
        return

    token = await read_file(token_filepath)

    auth_result = await authorise(stream_reader, stream_writer, token)
    if not auth_result:
        await aioconsole.aprint('Unknown token. Check it or re-register it.')
        return

    await submit_message(stream_writer, message, '\n')


if __name__ == '__main__':
    asyncio.run(main())
