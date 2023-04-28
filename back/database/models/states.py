from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class StateBase(SQLModel):
	status: bool
	marker: str
	entity_type: str
	entity_id: int


class States(StateBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: Optional[int] = Field(default=None, foreign_key="users.id")
	user: Optional["Users"] = Relationship(back_populates="states")


class StateCreate(StateBase):
	user_id: int


class StateRead(StateBase):
	id: int
	user_id: int


class StateReadWithRelations(StateRead):
	user: Optional["UserRead"] = None


class StateUpdate(SQLModel):
	status: Optional[bool] = None
	marker: Optional[str] = None
