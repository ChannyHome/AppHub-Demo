from fastapi import HTTPException, status

def require(condition: bool, msg: str = "Forbidden"):
    if not condition:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
