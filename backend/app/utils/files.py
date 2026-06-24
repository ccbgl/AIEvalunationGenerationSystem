import os
import aiofiles
from fastapi import UploadFile

UPLOAD_DIR = os.getenv('UPLOAD_DIR', '/app/upload')

async def save_upload_file(upload_file: UploadFile, dest_path: str) -> str:
    # ensure dir exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    async with aiofiles.open(dest_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return dest_path
