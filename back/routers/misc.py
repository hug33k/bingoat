from datetime import datetime
from fastapi import APIRouter, status
from pydantic import BaseModel, Field


router = APIRouter()


class Status(BaseModel):
	status: bool
	date: datetime = Field(default_factory=datetime.utcnow)


@router.get("/status", status_code=status.HTTP_200_OK, response_model=Status)
async def get_status():
	return Status(status=True)
