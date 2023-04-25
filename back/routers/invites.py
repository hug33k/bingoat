from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import InviteCreate, InviteRead, InviteUpdate, Invites, InviteReadWithRelations


router = APIRouter(
	prefix="/invites",
	tags=["invites"],
)


@router.get("", response_model=List[InviteRead])
async def get_invites():
	with get_session() as session:
		invites = session.exec(select(Invites)).all()
		return invites


@router.get("/{invite_id}", response_model=Union[InviteReadWithRelations, None])
async def get_invite(invite_id: int, session: Session = Depends(get_session)):
	invite = session.get(Invites, invite_id)
	if (not invite):
		raise HTTPException(status_code=404, detail="Invite not found")
	return invite


@router.post("", response_model=InviteRead, status_code=status.HTTP_201_CREATED)
async def add_invite(input_invite: InviteCreate):
	with get_session() as session:
		invite = Invites.from_orm(input_invite)
		session.add(invite)
		session.commit()
		session.refresh(invite)
		return invite


@router.post("/{invite_id}", response_model=InviteRead)
async def update_invite(input_invite: InviteUpdate, invite_id: int):
	with get_session() as session:
		invite = session.get(Invites, invite_id)
		if (not invite):
			raise HTTPException(status_code=404, detail="Invite not found")
		input_invite_dict = input_invite.dict(exclude_unset=True)
		for key, value in input_invite_dict.items():
			setattr(invite, key, value)
		session.add(invite)
		session.commit()
		session.refresh(invite)
		return invite


@router.post("/{invite_id}/accept", response_model=InviteRead)
async def accept_invite(invite_id: int):
	with get_session() as session:
		invite = session.get(Invites, invite_id)
		if (not invite):
			raise HTTPException(status_code=404, detail="Invite not found")
		setattr(invite, "accepted", True)
		session.add(invite)
		session.commit()
		session.refresh(invite)
		return invite


@router.post("/{invite_id}/refuse", response_model=InviteRead)
async def refuse_invite(invite_id: int):
	with get_session() as session:
		invite = session.get(Invites, invite_id)
		if (not invite):
			raise HTTPException(status_code=404, detail="Invite not found")
		setattr(invite, "accepted", False)
		session.add(invite)
		session.commit()
		session.refresh(invite)
		return invite


@router.delete("/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_invite(invite_id: int):
	with get_session() as session:
		invite = session.get(Invites, invite_id)
		if (not invite):
			raise HTTPException(status_code=404, detail="Invite not found")
		session.delete(invite)
		session.commit()
		return
