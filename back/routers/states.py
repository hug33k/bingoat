import json
from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from database import get_session, select, Session
from database.models import StateCreate, StateRead, StateUpdate, States, Cells, Zones
from websocket.manager import get_manager


router = APIRouter(
	prefix="/states",
	tags=["states"],
)


ws_manager = get_manager()


@router.get("", response_model=List[StateRead])
async def get_states():
	with get_session() as session:
		states = session.exec(select(States)).all()
		return states


@router.get("/{state_id}", response_model=Union[StateRead, None])
async def get_state(state_id: int, session: Session = Depends(get_session)):
	state = session.get(States, state_id)
	if (not state):
		raise HTTPException(status_code=404, detail="State not found")
	return state


@router.post("", response_model=StateRead, status_code=status.HTTP_201_CREATED)
async def add_state(input_state: StateCreate):
	with get_session() as session:
		state = States.from_orm(input_state)
		session.add(state)
		session.commit()
		session.refresh(state)
		return state


@router.post("/{state_id}", response_model=StateRead)
async def update_state(input_state: StateUpdate, state_id: int):
	with get_session() as session:
		try:
			state = session.get(States, state_id)
			if (not state):
				raise HTTPException(status_code=404, detail="State not found")
			input_state_dict = input_state.dict(exclude_unset=True)
			for key, value in input_state_dict.items():
				setattr(state, key, value)
			session.add(state)
			session.commit()
			session.refresh(state)
			grid_id = state.entity_id
			if (state.entity_type != "grid"):
				statement = ""
				if (state.entity_type == "cell"):
					statement = select(Cells).where(Cells.id == state.entity_id)
				elif (state.entity_type == "zone"):
					statement = select(Zones).where(Zones.id == state.entity_id)
				entity = session.exec(statement).first()
				grid_id = entity.grid_id
			return state
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error while updating state: ${e}")
		finally:
			await ws_manager.broadcast(grid_id, json.dumps(jsonable_encoder(state)))


@router.delete("/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_state(state_id: int):
	with get_session() as session:
		state = session.get(States, state_id)
		if (not state):
			raise HTTPException(status_code=404, detail="State not found")
		session.delete(state)
		session.commit()
		return
