import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def connection_manager(host, port):
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        yield reader, writer
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()
