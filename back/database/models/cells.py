from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from .cellszoneslink import CellsZonesLink
from .states import StateRead


class CellBase(SQLModel):
	name: str
	points: int
	position_x: int
	position_y: int


class Cells(CellBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	grid_id: Optional[int] = Field(default=None, foreign_key="grids.id")
	grid: Optional["Grids"] = Relationship(back_populates="cells")
	zones: List["Zones"] = Relationship(back_populates="cells", link_model=CellsZonesLink)


class CellCreate(CellBase):
	grid_id: int
	zones: List[int]


class CellRead(CellBase):
	id: int


class CellUpdate(SQLModel):
	name: Optional[str] = None
	points: Optional[int] = None
	position_x: Optional[int] = None
	position_y: Optional[int] = None
	grid_id: Optional[int] = None
	zones: Optional[List[int]] = None


class CellReadWithRelations(CellRead):
	grid: Optional["GridRead"] = None
	zones: Optional[List["ZoneRead"]] = None


class CellIdOnly(SQLModel):
	id: int


class CellReadWithStates(BaseModel):
	cell: CellRead
	states: List[StateRead]
