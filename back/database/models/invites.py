from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel


class InviteBase(SQLModel):
	desc: str
	accepted: Optional[bool] = None


class Invites(InviteBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	grid_id: Optional[int] = Field(default=None, foreign_key="grids.id")
	grid: Optional["Grids"] = Relationship(back_populates="invites")
	author_id: Optional[int] = Field(default=None, foreign_key="users.id")
	author: Optional["Users"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Users.id==Invites.author_id", "lazy": "select"})
	guest_id: Optional[int] = Field(default=None, foreign_key="users.id")
	guest: Optional["Users"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Users.id==Invites.guest_id", "lazy": "select"})


class InviteCreate(InviteBase):
	pass


class InviteRead(InviteBase):
	id: int


class InviteReadWithRelations(InviteRead):
	grid: Optional["GridRead"] = []
	author: Optional["UserRead"] = []
	guest: Optional["UserRead"] = []


class InviteUpdate(SQLModel):
	desc: Optional[str] = None
	accepted: Optional[bool] = None
