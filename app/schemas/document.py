from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trainer_id: str
    filename: str
    storage_path: str
    content_type: str
    category: str
    status: str
    created_at: datetime