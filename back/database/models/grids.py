from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from .states import StateRead


class GridBase(SQLModel):
	name: str
	published: bool


class Grids(GridBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	cells: List["Cells"] = Relationship(back_populates="grid")
	zones: List["Zones"] = Relationship(back_populates="grid")
	owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
	owner: Optional["Users"] = Relationship(back_populates="grids")
	invites: Optional["Invites"] = Relationship(back_populates="grid")


class GridCreate(GridBase):
	owner_id: int


class GridRead(GridBase):
	id: int


class GridUpdate(SQLModel):
	name: Optional[str] = None
	published: Optional[bool] = None
	owner_id: Optional[int] = None


class GridReadWithRelations(GridRead):
	cells: List["CellRead"] = []
	zones: List["ZoneReadWithCells"] = []
	owner: Optional["Users"] = None


class GridReadWithStates(BaseModel):
	grid: GridRead
	states: List[StateRead]
