from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from backend.app.deps import get_current_user
from backend.app.utils.files import save_upload_file
from backend.app.core.config import settings
import os

router = APIRouter(prefix='/api/files', tags=['files'])

@router.post('/upload')
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # store under backend/app/static/upload/<user_id>/...
    filename = file.filename
    user_id = current_user['id']
    # default upload dir inside static so files are served by StaticFiles
    dest_dir = os.getenv('UPLOAD_DIR', 'backend/app/static/upload')
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"user_{user_id}_{filename}")
    await save_upload_file(file, dest_path)
    # return web-accessible path
    web_path = '/static/upload/' + os.path.basename(dest_path)
    return {"path": web_path}
