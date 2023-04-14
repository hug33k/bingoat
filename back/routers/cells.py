from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import CellCreate, CellRead, CellUpdate, Cells, CellReadWithRelations


router = APIRouter(
	prefix="/cells",
	tags=["cells"],
)


@router.get("", response_model=List[CellRead])
async def get_cells():
	with get_session() as session:
		cells = session.exec(select(Cells)).all()
		return cells


@router.get("/{cell_id}", response_model=Union[CellReadWithRelations, None])
async def get_cell(cell_id: int, session: Session = Depends(get_session)):
	cell = session.get(Cells, cell_id)
	if (not cell):
		raise HTTPException(status_code=404, detail="Cell not found")
	return cell


@router.post("", response_model=CellRead, status_code=status.HTTP_201_CREATED)
async def add_cell(input_cell: CellCreate):
	with get_session() as session:
		cell = Cells.from_orm(input_cell)
		session.add(cell)
		session.commit()
		session.refresh(cell)
		return cell


@router.post("/{cell_id}", response_model=CellRead)
async def update_cell(input_cell: CellUpdate, cell_id: int):
	with get_session() as session:
		cell = session.get(Cells, cell_id)
		if (not cell):
			raise HTTPException(status_code=404, detail="Cell not found")
		input_cell_dict = input_cell.dict(exclude_unset=True)
		for key, value in input_cell_dict.items():
			setattr(cell, key, value)
		session.add(cell)
		session.commit()
		session.refresh(cell)
		return cell


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cell(cell_id: int):
	with get_session() as session:
		cell = session.get(Cells, cell_id)
		if (not cell):
			raise HTTPException(status_code=404, detail="Cell not found")
		session.delete(cell)
		session.commit()
		return
