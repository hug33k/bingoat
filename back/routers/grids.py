from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import GridCreate, GridRead, GridUpdate, Grids, GridReadWithRelations, GridReadWithStates, States


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


@router.get("/state/{grid_id}", response_model=GridReadWithStates)
async def get_grid_states(grid_id: int, user:Union[str, None] = None, session: Session = Depends(get_session)):
	print(user, grid_id)
	grid = session.get(Grids, grid_id)
	if (not grid):
		raise HTTPException(status_code=404, detail="Grid not found")
	statement = select(States).where(States.entity_type == "grid",
									States.entity_id == grid_id)
	if (user is not None):
		statement = statement.where(States.user == user)
	states = session.exec(statement)
	return { "grid": grid, "states": states.all() }
