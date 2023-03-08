import asyncio
import logging
import os
import socket
import sys
import tkinter
from typing import Dict
import anyio

from async_timeout import timeout
from anyio import Path, create_task_group

from arg_parsers import create_client_parser
from chat_api import authorise, read_chat, register
from context_managers import connection_manager
from exceptions import InvalidTokenError, TokenDoesNotExistError
from gui import (
    NicknameReceived,
    ReadConnectionStateChanged,
    SendingConnectionStateChanged,
    TkAppClosed,
    draw,
    show_registration_window,
)
from record_chat_history import save_message
from sender import read_token, run_sender
from utils import write_file


watchdog_logger = logging.getLogger(__file__)


async def ping_pong(host, port) -> None:
    while True:
        async with connection_manager(host, port) as streams:
            stream_reader, _ = streams

            async with timeout(1):
                await stream_reader.readline()

        await asyncio.sleep(5)


async def watch_for_connection(watchdog_queue: asyncio.Queue) -> None:
    while True:
        event = await watchdog_queue.get()
        watchdog_logger.info(event)


async def read_messages(
    host: str,
    reading_port: str,
    queues: Dict[str, asyncio.Queue],
    history_filepath: str,
) -> None:
    watchdog_queue, messages_queue = queues['watchdog'], queues['messages']
    async for message in read_chat(host, reading_port, queues):
        await save_message(message, history_filepath)
        watchdog_queue.put_nowait('New message in chat')
        messages_queue.put_nowait(message)


async def handle_connections(
    host: str,
    sending_port: str,
    reading_port: str,
    history_filepath: str,
    queues: Dict[str, asyncio.Queue],
) -> None:
    while True:
        try:
            async with create_task_group() as task_group:
                task_group.start_soon(watch_for_connection, queues['watchdog'])
                task_group.start_soon(ping_pong, host, sending_port)
                task_group.start_soon(read_messages, host, reading_port, queues, history_filepath)
                task_group.start_soon(run_sender, host, sending_port, queues)
        except (ConnectionError, socket.gaierror, anyio.ExceptionGroup):
            queues['watchdog'].put_nowait(
                'There\'s a problem with the network. Let\'s try to reconnect...',
            )
            queues['status_updates'].put_nowait(SendingConnectionStateChanged.CLOSED)
            queues['status_updates'].put_nowait(ReadConnectionStateChanged.CLOSED)
            await asyncio.sleep(5)


async def auth_user(host: str, port: str, queues: asyncio.Queue) -> None:
    while True:
        try:
            token = await read_token()
            user = await authorise(host, port, token)
            break
        except (TokenDoesNotExistError, InvalidTokenError):
            nickname = await show_registration_window(queues)
            user = await register(host, port, nickname=nickname)
            token_filepath = os.path.join(await Path(__file__).parent.parent.resolve(), '.token')
            await write_file(user['account_hash'], token_filepath)
            break
        except socket.gaierror:
            watchdog_logger.info(
                'There\'s a problem with the network. Let\'s try to reconnect...',
            )
            await asyncio.sleep(5)

    nickname = user['nickname']
    queues['status_updates'].put_nowait(NicknameReceived(nickname))
    queues['watchdog'].put_nowait(f'Authorization is complete. User: {nickname}.')


async def main() -> None:
    logging.basicConfig(
        format='[%(created)d]: %(message)s',
        level=logging.DEBUG,
    )

    parser = create_client_parser()
    args = parser.parse_args()
    chat_host, sending_port, reading_port, history_filepath = (
        args.host,
        args.sending_port,
        args.reading_port,
        args.history,
    )

    queue_names = ['messages', 'sending', 'status_updates', 'watchdog']
    queues = {queue_name: asyncio.Queue() for queue_name in queue_names}

    await auth_user(chat_host, sending_port, queues)

    try:
        async with create_task_group() as task_group:
            task_group.start_soon(draw, queues)
            task_group.start_soon(
                handle_connections,
                chat_host,
                sending_port,
                reading_port,
                history_filepath,
                queues,
            )
    except (TkAppClosed, KeyboardInterrupt):
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
