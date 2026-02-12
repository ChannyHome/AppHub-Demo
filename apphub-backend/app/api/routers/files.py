from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

router = APIRouter(prefix="/files", tags=["files"])
BASE_DIR = Path("storage/images")
BASE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Not allowed extension: {ext}")
    
    new_name = f"{uuid.uuid4().hex}{ext}"
    save_path = BASE_DIR / new_name
    
    data = await file.read()
    save_path.write_bytes(data)
    
    #프론트가 바로 쓸 URL 경로(상대경로)를 리턴
    return {"filename": new_name, "url_path": f"/static/images/{new_name}"}
      