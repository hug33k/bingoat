from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from database import get_session, select, Session
from database.models import UserCreate, UserRead, UserUpdate, Users, UserReadWithRelations


router = APIRouter(
	prefix="/users",
	tags=["users"],
)


@router.get("", response_model=List[UserRead])
async def get_users():
	with get_session() as session:
		users = session.exec(select(Users)).all()
		return users


@router.get("/{user_id}", response_model=Union[UserReadWithRelations, None])
async def get_user(user_id: int, session: Session = Depends(get_session)):
	user = session.get(Users, user_id)
	if (not user):
		raise HTTPException(status_code=404, detail="User not found")
	return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(input_user: UserCreate):
	with get_session() as session:
		user = Users.from_orm(input_user)
		session.add(user)
		session.commit()
		session.refresh(user)
		return user


@router.post("/{user_id}", response_model=UserRead)
async def update_user(input_user: UserUpdate, user_id: int):
	with get_session() as session:
		user = session.get(Users, user_id)
		if (not user):
			raise HTTPException(status_code=404, detail="User not found")
		input_user_dict = input_user.dict(exclude_unset=True)
		for key, value in input_user_dict.items():
			if not value:
				continue
			setattr(user, key, value)
		session.add(user)
		session.commit()
		session.refresh(user)
		return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: int):
	with get_session() as session:
		user = session.get(Users, user_id)
		if (not user):
			raise HTTPException(status_code=404, detail="User not found")
		session.delete(user)
		session.commit()
		return
