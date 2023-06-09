from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .states import StateRead
from .cellszoneslink import CellsZonesLink


class ZoneBase(SQLModel):
	name: str
	points: int


class Zones(ZoneBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	grid_id: Optional[int] = Field(default=None, foreign_key="grids.id")
	grid: Optional["Grids"] = Relationship(back_populates="zones")
	# TODO: cells_id?
	cells: List["Cells"] = Relationship(back_populates="zones", link_model=CellsZonesLink)


class ZoneCreate(ZoneBase):
	grid_id: int
	cells: List[int]


class ZoneRead(ZoneBase):
	id: int


class ZoneUpdate(SQLModel):
	name: Optional[str] = None
	points: Optional[int] = None
	grid_id: Optional[int] = None
	cells: Optional[List[int]] = None


class ZoneReadWithRelations(ZoneRead):
	grid: Optional["GridRead"] = None
	cells: Optional[List["CellRead"]] = None


class ZoneReadWithCells(ZoneRead):
	cells: List["CellIdOnly"]


class ZoneReadWithStates(SQLModel):
	zone: ZoneRead
	states: List[StateRead]
