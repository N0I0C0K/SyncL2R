from pydantic import BaseModel


class HistoryModal(BaseModel):
    time: str
    message: str
