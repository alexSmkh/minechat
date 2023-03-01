import os
from pathlib import Path
import aiofiles

from exceptions import TokenDoesNotExistError


async def write_file(text: str, filepath: str, mode: str = 'w') -> None:
    async with aiofiles.open(filepath, mode=mode) as file:
        await file.write(text)


async def read_file(filepath: str, mode='r') -> str:
    async with aiofiles.open(filepath, mode) as file:
        content = await file.read()
    return content


async def read_token() -> str:
    token_filepath = os.path.join(Path(__file__).parent.parent.resolve(), '.token')
    if os.path.isfile(token_filepath):
        return await read_file(token_filepath)
    raise TokenDoesNotExistError('You do not have a token. Please register')
