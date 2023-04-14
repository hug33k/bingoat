from typing import Optional
from sqlmodel import Field, SQLModel


class CellsZonesLink(SQLModel, table=True):
	cell_id: Optional[int] = Field(
		default=None, foreign_key="cells.id", primary_key=True
	)
	zone_id: Optional[int] = Field(
		default=None, foreign_key="zones.id", primary_key=True
	)
