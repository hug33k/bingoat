from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import ZoneCreate, ZoneRead, ZoneUpdate, Zones, ZoneReadWithRelations


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
	if (not zone):
		raise HTTPException(status_code=404, detail="Zone not found")
	return zone


@router.post("", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
async def add_zone(input_zone: ZoneCreate):
	with get_session() as session:
		zone = Zones.from_orm(input_zone)
		session.add(zone)
		session.commit()
		session.refresh(zone)
		return zone


@router.post("/{zone_id}", response_model=ZoneRead)
async def update_zone(input_zone: ZoneUpdate, zone_id: int):
	with get_session() as session:
		zone = session.get(Zones, zone_id)
		if (not zone):
			raise HTTPException(status_code=404, detail="Zone not found")
		input_zone_dict = input_zone.dict(exclude_unset=True)
		for key, value in input_zone_dict.items():
			setattr(zone, key, value)
		session.add(zone)
		session.commit()
		session.refresh(zone)
		return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_zone(zone_id: int):
	with get_session() as session:
		zone = session.get(Zones, zone_id)
		if (not zone):
			raise HTTPException(status_code=404, detail="Zone not found")
		session.delete(zone)
		session.commit()
		return
