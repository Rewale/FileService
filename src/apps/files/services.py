import aiofiles as aiof


async def save_file(content: bytes, path: str):
    async with aiof.open(path, 'wb') as out:
        await out.write(content)
        await out.flush()
