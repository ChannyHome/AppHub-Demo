from pydantic import BaseModel

class BatchRunRequest(BaseModel):
    metric_date: str  # 'YYYY-MM-DD'
