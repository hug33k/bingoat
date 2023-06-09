from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class UserBase(SQLModel):
	username: str
	password: str
	admin: bool = False


class Users(UserBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	grids: List["Grids"] = Relationship(back_populates="owner")
	states: List["States"] = Relationship(back_populates="user")
	invites_sent: List["Invites"] = Relationship(sa_relationship_kwargs={
													"primaryjoin": "Users.id==Invites.author_id",
													"lazy": "select", "viewonly": True})
	invites_received: List["Invites"] = Relationship(sa_relationship_kwargs={
													"primaryjoin": "Users.id==Invites.guest_id",
													"lazy": "select", "viewonly": True})


class UserCreate(SQLModel):
	username: str
	password: str


class UserRead(SQLModel):
	id: int
	username: str


class UserReadWithRelations(UserRead):
	grids: List["GridRead"] = []
	states: List["StateRead"] = []
	invites_sent: List["InviteReadWithRelations"] = []
	invites_received: List["InviteReadWithRelations"] = []


class UserUpdate(SQLModel):
	username: Optional[str] = None
