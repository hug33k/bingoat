from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import GridCreate, GridRead, GridUpdate, Grids, GridReadWithRelations, GridReadWithStates, States
from .cells import get_cell_states
from .zones import get_zone_states
from .states import generate_grid_state


router = APIRouter(
	prefix="/grids",
	tags=["grids"],
)


@router.get("", response_model=List[GridRead])
async def get_grids():
	with get_session() as session:
		grids = session.exec(select(Grids)).all()
		return grids


@router.get("/{grid_id}", response_model=Union[GridReadWithRelations, None])
async def get_grid(grid_id: int, session: Session = Depends(get_session)):
	grid = session.get(Grids, grid_id)
	if (not grid):
		raise HTTPException(status_code=404, detail="Grid not found")
	return grid


@router.post("", response_model=GridRead, status_code=status.HTTP_201_CREATED)
async def add_grid(input_grid: GridCreate):
	with get_session() as session:
		grid = Grids.from_orm(input_grid)
		session.add(grid)
		session.commit()
		session.refresh(grid)
		return grid


@router.post("/{grid_id}", response_model=GridRead)
async def update_grid(input_grid: GridUpdate, grid_id: int):
	with get_session() as session:
		grid = session.get(Grids, grid_id)
		if (not grid):
			raise HTTPException(status_code=404, detail="Grid not found")
		input_grid_dict = input_grid.dict(exclude_unset=True)
		for key, value in input_grid_dict.items():
			setattr(grid, key, value)
		session.add(grid)
		session.commit()
		session.refresh(grid)
		return grid


@router.delete("/{grid_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_grid(grid_id: int):
	with get_session() as session:
		grid = session.get(Grids, grid_id)
		if (not grid):
			raise HTTPException(status_code=404, detail="Grid not found")
		session.delete(grid)
		session.commit()
		return

@router.post("/{grid_id}/publish", response_model=GridRead)
async def publish_grid(grid_id: int):
	with get_session() as session:
		grid = session.get(Grids, grid_id)
		if (not grid):
			raise HTTPException(status_code=404, detail="Grid not found")
		if (grid.published):
			raise HTTPException(status_code=403, detail="Grid already published")
		grid.published = True
		session.add(grid)
		session.commit()
		session.refresh(grid)
		return grid


@router.get("/{grid_id}/state", response_model=GridReadWithStates)
async def get_grid_states(grid_id: int, user:Union[str, None] = None, session: Session = Depends(get_session)):
	grid = session.get(Grids, grid_id)
	if (not grid):
		raise HTTPException(status_code=404, detail="Grid not found")
	statement = select(States).where(States.entity_type == "grid",
									States.entity_id == grid_id)
	if (user is not None):
		statement = statement.where(States.user == user)
	states = session.exec(statement)
	return { "grid": grid, "states": states.all() }


@router.post("/{grid_id}/state/generate", response_model=GridReadWithStates, status_code=status.HTTP_201_CREATED)
async def generate_grid_states(grid_id: int, user:str, session: Session = Depends(get_session)):
	await generate_grid_state(grid_id, user, session)
	return await get_grid_states(grid_id, user, session)


async def check_grid(grid_id: int, user: str):
	with get_session() as session:
		grid = session.get(Grids, grid_id)
		status = True
		for cell in grid.cells:
			res = await get_cell_states(cell.id, user, session)
			states = res["states"]
			for state in states:
				if (not state.status):
					status = False
		for zone in grid.zones:
			res = await get_zone_states(zone.id, user, session)
			states = res["states"]
			for state in states:
				if (not state.status):
					status = False
		res = await get_grid_states(grid_id, user, session)
		states = res["states"]
		updated = []
		for state in states:
			if (state.status != status):
				updated.append(state)
			state.status = status
			session.add(state)
		session.commit()
		for state in states:
			session.refresh(state)
		return updated
