from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from .state import StateRead, StateUpdate


class GridBase(SQLModel):
	name: str


class Grids(GridBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	cells: List["Cells"] = Relationship(back_populates="grid")
	zones: List["Zones"] = Relationship(back_populates="grid")


class GridCreate(GridBase):
	pass


class GridRead(GridBase):
	id: int


class GridUpdate(SQLModel):
	name: Optional[str] = None


class GridReadWithRelations(GridRead):
	cells: List["CellRead"] = []
	zones: List["ZoneReadWithCells"] = []


class GridReadWithStates(BaseModel):
	grid: GridRead
	states: List[StateRead]
