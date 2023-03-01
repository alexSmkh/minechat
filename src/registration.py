import asyncio
import os
from pathlib import Path

import aioconsole

from arg_parsers import create_registration_parser
from chat_api import register
from utils import write_file


async def main() -> None:
    parser = create_registration_parser()
    args = parser.parse_args()
    host, port = args.host, args.sending_port

    registered_user_data = await register(host, port)

    token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
    await write_file(registered_user_data['account_hash'], token_filepath)

    successful_message = (
        'You have successfully registered!\n'
        f'Your nickname: {registered_user_data["nickname"]}\n'
        f'Your token: {registered_user_data["account_hash"]}\n'
        f'Your token is successfully written to the {token_filepath} file'
    )
    await aioconsole.aprint(successful_message)


if __name__ == '__main__':
    asyncio.run(main())
