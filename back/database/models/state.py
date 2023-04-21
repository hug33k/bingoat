from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class StateBase(SQLModel):
	user: str
	status: bool
	marker: str
	entity_type: str
	entity_id: int


class States(StateBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)


class StateCreate(StateBase):
	pass


class StateRead(StateBase):
	id: int


class StateUpdate(SQLModel):
	status: Optional[bool] = None
	marker: Optional[str] = None
