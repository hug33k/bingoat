from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import ZoneCreate, ZoneRead, ZoneUpdate, \
							Zones, ZoneReadWithRelations, ZoneReadWithStates, \
							States, Cells
from .cells import get_cell_states
from .states import check_states, update_states
from .grids import get_grid_and_check_if_editable


router = APIRouter(
	prefix="/zones",
	tags=["zones"],
)


@router.get("", response_model=List[ZoneRead])
async def get_zones():
	with get_session() as session:
		zones = session.exec(select(Zones)).all()
		return zones


@router.get("/{zone_id}", response_model=Union[ZoneReadWithRelations, None])
async def get_zone(zone_id: int, session: Session = Depends(get_session)):
	zone = session.get(Zones, zone_id)
	if not zone:
		raise HTTPException(status_code=404, detail="Zone not found")
	return zone


@router.post("", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
async def add_zone(input_zone: ZoneCreate):
	with get_session() as session:
		zone = Zones.from_orm(input_zone)
		get_grid_and_check_if_editable(zone.grid_id, session)
		if input_zone.cells:
			statement = select(Cells).where(Cells.id.in_(input_zone.cells))
			cells = session.exec(statement).all()
			zone.cells = cells
		session.add(zone)
		session.commit()
		session.refresh(zone)
		return zone


@router.post("/{zone_id}", response_model=ZoneRead)
async def update_zone(input_zone: ZoneUpdate, zone_id: int):
	with get_session() as session:
		zone = session.get(Zones, zone_id)
		if not zone:
			raise HTTPException(status_code=404, detail="Zone not found")
		input_zone_dict = input_zone.dict(exclude_unset=True)
		for key, value in input_zone_dict.items():
			if (key == "grid_id" and value != zone.grid_id):
				get_grid_and_check_if_editable(value, session)
				setattr(zone, key, value)
			if key == "cells":
				statement = select(Cells).where(Cells.id.in_(value))
				cells = session.exec(statement).all()
				setattr(zone, key, cells)
			else:
				setattr(zone, key, value)
		session.add(zone)
		session.commit()
		session.refresh(zone)
		return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_zone(zone_id: int):
	with get_session() as session:
		zone = session.get(Zones, zone_id)
		if not zone:
			raise HTTPException(status_code=404, detail="Zone not found")
		session.delete(zone)
		session.commit()
		return


@router.get("/{zone_id}/state", response_model=ZoneReadWithStates)
async def get_zone_states(zone_id: int, user:Union[str, None] = None,
							session: Session = Depends(get_session)):
	zone = session.get(Zones, zone_id)
	if not zone:
		raise HTTPException(status_code=404, detail="Zone not found")
	statement = select(States).where(States.entity_type == "zone",
									States.entity_id == zone_id)
	if user is not None:
		statement = statement.where(States.user == user)
	states = session.exec(statement)
	return { "zone": zone, "states": states.all() }


async def check_zone(zone_id: int, user:str):
	with get_session() as session:
		zone = session.get(Zones, zone_id)
		state_status = True
		for cell in zone.cells:
			res = await get_cell_states(cell.id, user, session)
			state_status = check_states(res["states"], state_status)
		res = await get_zone_states(zone_id, user, session)
		return await update_states(res["states"], state_status, session)
