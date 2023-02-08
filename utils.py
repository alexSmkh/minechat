import aiofiles


async def write_file(text: str, filepath: str, mode: str = 'w') -> None:
    async with aiofiles.open(filepath, mode=mode) as file:
        await file.write(text)


async def read_file(filepath: str, mode='r') -> str:
    async with aiofiles.open(filepath, mode) as file:
        content = await file.read()
    return content
