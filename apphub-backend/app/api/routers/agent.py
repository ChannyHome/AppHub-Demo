# app/api/routers/agent.py
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/agent", tags=["agent"])

# 프로젝트 루트(apphub-backend) 기준: agent/setup/AppHubAgent.Setup.msi
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SETUP_FILE = PROJECT_ROOT / "agent" / "setup" / "AppHubAgent.Setup.msi"


@router.get("/download-setup")
async def download_setup(): 
    if not SETUP_FILE.exists() or not SETUP_FILE.is_file():
        raise HTTPException(
          status_code=404, 
          detail=f"Agent setup file not found: {SETUP_FILE}"
          )

    return FileResponse(
        path=str(SETUP_FILE),
        filename=SETUP_FILE.name, # 다운로드 파일명
        media_type="application/octet-stream",
    )
