from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import CellCreate, CellRead, CellUpdate, Cells, CellReadWithRelations, CellReadWithStates, States, StateUpdate, Zones, Grids
from .states import update_state


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
		grid = session.get(Grids, cell.grid_id)
		if (not grid):
			raise HTTPException(status_code=404, detail="Grid not found")
		if (grid.published):
			raise HTTPException(status_code=403, detail="Grid already published")
		if (input_cell.zones):
			statement = select(Zones).where(Zones.id.in_(input_cell.zones))
			zones = session.exec(statement).all()
			cell.zones = zones
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
			if (key == "grid_id" and value != cell.grid_id):
				grid = session.get(Grids, value)
				if (not grid):
					raise HTTPException(status_code=404, detail="Grid not found")
				if (grid.published):
					raise HTTPException(status_code=403, detail="Grid already published")
				setattr(cell, key, value)
			if (key == "zones"):
				statement = select(Zones).where(Zones.id.in_(value))
				zones = session.exec(statement).all()
				setattr(cell, key, zones)
			else:
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


@router.get("/{cell_id}/state", response_model=CellReadWithStates)
async def get_cell_states(cell_id: int, user:Union[str, None] = None, session: Session = Depends(get_session)):
	cell = session.get(Cells, cell_id)
	if (not cell):
		raise HTTPException(status_code=404, detail="Cell not found")
	statement = select(States).where(States.entity_type == "cell",
									States.entity_id == cell_id)
	if (user is not None):
		statement = statement.where(States.user == user)
	states = session.exec(statement)
	return { "cell": cell, "states": states.all() }


@router.post("/{cell_id}/state", response_model=CellReadWithStates)
async def update_cell_states(input_state: StateUpdate, cell_id: int, user:str, session: Session = Depends(get_session)):
	statement = select(States).where(States.entity_type == "cell",
									States.entity_id == cell_id,
									States.user == user)
	state = session.exec(statement).one()
	await update_state(input_state, state.id, session)
	return await get_cell_states(cell_id, user, session)
