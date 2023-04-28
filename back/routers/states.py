import json
from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from database import get_session, select, Session
from database.models import StateCreate, StateRead, StateUpdate, States, \
							Cells, Zones, Grids, StateReadWithRelations
from websocket.manager import Manager


router = APIRouter(
	prefix="/states",
	tags=["states"],
)


# Make it private
@router.get("", response_model=List[StateRead])
async def get_states():
	with get_session() as session:
		states = session.exec(select(States)).all()
		return states


# Make it private
@router.get("/{state_id}", response_model=Union[StateReadWithRelations, None])
async def get_state(state_id: int, session: Session = Depends(get_session)):
	state = session.get(States, state_id)
	if not state:
		raise HTTPException(status_code=404, detail="State not found")
	return state


# Make it private
@router.post("", response_model=StateRead, status_code=status.HTTP_201_CREATED)
async def add_state(input_state: StateCreate):
	with get_session() as session:
		state = States.from_orm(input_state)
		session.add(state)
		session.commit()
		session.refresh(state)
		return state


# Make it private
@router.post("/{state_id}", response_model=StateRead)
async def update_state(input_state: StateUpdate, state_id: int,
						session: Session = Depends(get_session)):
	try:
		state = session.get(States, state_id)
		if not state:
			raise HTTPException(status_code=404, detail="State not found")
		input_state_dict = input_state.dict(exclude_unset=True)
		for key, value in input_state_dict.items():
			setattr(state, key, value)
		session.add(state)
		session.commit()
		session.refresh(state)
		return state
	finally:
		if state:
			await check_state_parents(state)


# Make it private
@router.delete("/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_state(state_id: int):
	with get_session() as session:
		state = session.get(States, state_id)
		if not state:
			raise HTTPException(status_code=404, detail="State not found")
		session.delete(state)
		session.commit()
		return


async def check_state_parents(state: StateRead):
	from .zones import check_zone
	from .grids import check_grid
	with get_session() as session:
		updates = [state]
		grid_id = None
		if state.entity_type == "cell":
			cell = session.get(Cells, state.entity_id)
			grid_id = cell.grid_id
			if cell.zones:
				for zone in cell.zones:
					states = await check_zone(zone.id, state.user)
					if states:
						updates.extend(states)
			states = await check_grid(grid_id, state.user)
			if states:
				updates.extend(states)
		elif state.entity_type == "zone":
			zone = session.get(Zones, state.entity_id)
			grid_id = zone.grid_id
			states = await check_grid(grid_id, state.user)
			if states:
				updates.extend(states)
		elif state.entity_type == "grid":
			grid_id = state.entity_id
		for update in updates:
			ws_manager = Manager.get_instance()
			await ws_manager.broadcast(grid_id, json.dumps(jsonable_encoder(update)))


async def generate_grid_state(grid_id: int, user_id:int, session: Session = Depends(get_session)):
	async def check_if_entity_state_exists(entity_type, entity_id):
		existing_entity_state_statement = select(States).where(States.entity_type == entity_type,
															States.entity_id == entity_id,
															States.user_id == user_id)
		existing_entity_state = session.exec(existing_entity_state_statement).all()
		return bool(len(existing_entity_state))

	grid = session.get(Grids, grid_id)
	if not grid:
		raise HTTPException(status_code=404, detail="Grid not found")

	if not await check_if_entity_state_exists("grid", grid.id):
		grid_state = States(user_id=user_id, status=False, marker="",
							entity_type="grid", entity_id=grid.id)
		await add_state(grid_state)

	cells = session.exec(select(Cells).where(Cells.grid_id == grid.id)).all()
	for cell in cells:
		cell_exists = await check_if_entity_state_exists("cell", cell.id)
		if not cell_exists:
			cell_state = States(user_id=user_id, status=False, marker="",
								entity_type="cell", entity_id=cell.id)
			await add_state(cell_state)

	zones = session.exec(select(Zones).where(Zones.grid_id == grid.id)).all()
	for zone in zones:
		zone_exists = await check_if_entity_state_exists("zone", zone.id)
		if not zone_exists:
			zone_state = States(user_id=user_id, status=False, marker="",
								entity_type="zone", entity_id=zone.id)
			await add_state(zone_state)


def check_states(states: List[StateRead], state_status: bool):
	for state in states:
		if not state.status:
			state_status = False
	return state_status


async def update_states(states: List[StateRead], state_status: bool, session: Session):
	updated = []
	for state in states:
		if state.status != state_status:
			updated.append(state)
			state.status = state_status
		session.add(state)
	session.commit()
	for state in states:
		session.refresh(state)
	return updated
