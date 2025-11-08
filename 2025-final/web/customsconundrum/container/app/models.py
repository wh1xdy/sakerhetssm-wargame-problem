from pydantic import BaseModel
from datetime import datetime


class Declaration(BaseModel):
    id: int
    entry_date: str
    country_origin: str
    item_name: str
    description: str
    quantity: int
    value: float
    category: str
    status: str
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True
