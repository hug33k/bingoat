from datetime import datetime
from fastapi import APIRouter, status
from sqlmodel import Field, SQLModel


router = APIRouter()


class Status(SQLModel):
	status: bool
	date: datetime = Field(default_factory=datetime.utcnow)


@router.get("/status", status_code=status.HTTP_200_OK, response_model=Status)
async def get_status():
	return Status(status=True)
