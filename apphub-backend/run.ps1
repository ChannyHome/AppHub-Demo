# 현재 스크립트 위치
# $root = Split-Path -Parent $MyInvocation.MyCommand.Path
# venv 활성화 (dot sourcing 필수)
# . "$root\venv\Scripts\Activate.ps1"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$root\.venv\Scripts\Activate.ps1"
python -m pip install pydantic-settings
$env:PYTHONPATH="."
uvicorn app.main:app --host 0.0.0.0 --port 8500 --reload
