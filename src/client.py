import asyncio
import logging
import socket
import sys

from async_timeout import Timeout, timeout, timeout_at

from arg_parsers import create_client_parser, create_record_history_parser
from chat_api import authorise, read_chat
from context_managers import connection_manager
from exceptions import InvalidTokenError, TokenDoesNotExistError
from gui import (
    NicknameReceived,
    ReadConnectionStateChanged,
    SendingConnectionStateChanged,
    draw,
    show_alert,
)
from record_chat_history import save_message
from sender import read_token, run_sender


watchdog_logger = logging.getLogger(__file__)


async def ping_pong(host, port) -> None:
    while True:
        async with connection_manager(host, port) as streams:
            stream_reader, _ = streams

            async with timeout(1):
                await stream_reader.readline()

        await asyncio.sleep(5)


async def watch_for_connection(watchdog_queue):
    while True:
        event = await watchdog_queue.get()
        watchdog_logger.info(event)


async def read_messages(
    host: str,
    reading_port: str,
    reading_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue,
    history_filepath: str,
) -> None:
    async for message in read_chat(host, reading_port):
        await save_message(message, history_filepath)
        watchdog_queue.put_nowait('New message in chat')
        reading_queue.put_nowait(message)


async def send_messages(
    host: str,
    port: str,
    sending_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue,
    status_updates_queue: asyncio.Queue,
) -> None:
    token = await read_token()
    user = await authorise(host, port, token)
    nickname = user['nickname']

    status_updates_queue.put_nowait(NicknameReceived(nickname))
    watchdog_queue.put_nowait(f'Authorization is complete. User: {nickname}.')

    await run_sender(host, port, token, sending_queue=sending_queue, watchdog_queue=watchdog_queue)


async def handle_connections(
    host: str,
    sending_port: str,
    reading_port: str,
    messages_queue: asyncio.Queue,
    sending_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue,
    history_filepath: str,
    status_updates_queue: asyncio.Queue,
) -> None:
    status_updates_queue.put_nowait(SendingConnectionStateChanged.INITIATED)
    status_updates_queue.put_nowait(ReadConnectionStateChanged.INITIATED)

    while True:
        try:
            watchdog_queue.put_nowait('Connect to the server')
            status_updates_queue.put_nowait(SendingConnectionStateChanged.ESTABLISHED)
            status_updates_queue.put_nowait(ReadConnectionStateChanged.ESTABLISHED)
            await asyncio.gather(
                watch_for_connection(watchdog_queue),
                ping_pong(host, sending_port),
                read_messages(host, reading_port, messages_queue, watchdog_queue, history_filepath),
                send_messages(
                    host,
                    sending_port,
                    sending_queue,
                    watchdog_queue,
                    status_updates_queue,
                ),
            )
        except TokenDoesNotExistError:
            watchdog_queue.put_nowait('Failed authorization')
            status_updates_queue.put_nowait(SendingConnectionStateChanged.CLOSED)
            show_alert('Token doesn\'t exist', 'Please register')
            return
        except InvalidTokenError:
            watchdog_queue.put_nowait('Failed authorization')
            status_updates_queue.put_nowait(SendingConnectionStateChanged.CLOSED)
            show_alert('Invalid token', 'Please check the token or re-register again')
            return
        except (ConnectionError, socket.gaierror):
            status_updates_queue.put_nowait(SendingConnectionStateChanged.CLOSED)
            status_updates_queue.put_nowait(ReadConnectionStateChanged.CLOSED)
            await asyncio.sleep(5)


async def main() -> None:
    logging.basicConfig(
        format='[%(created)d] Event %(message)s',
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

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    try:
        await asyncio.gather(
            draw(messages_queue, sending_queue, status_updates_queue),
            handle_connections(
                chat_host,
                sending_port,
                reading_port,
                messages_queue,
                sending_queue,
                watchdog_queue,
                history_filepath,
                status_updates_queue,
            ),
        )
    except asyncio.CancelledError as err:
        print(err, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
