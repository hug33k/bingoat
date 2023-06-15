from datetime import timedelta, datetime
from typing import List, Union
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import SQLModel
from database import get_session, select, Session
from database.models import UserCreate, UserRead, UserUpdate, Users, UserReadWithRelations


router = APIRouter(
	prefix="/users",
	tags=["users"],
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(SQLModel):
	access_token: str
	token_type: str


class TokenData(SQLModel):
	id: Union[int, None] = None
	username: Union[str, None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
	return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def decode_token(token):
	return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

async def get_current_user(token: str = Depends(oauth2_scheme),
							session: Session = Depends(get_session)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		data = decode_token(token)
		username: str = data["sub"]
		user_id: int = data["id"]
		if username is None or id is None:
			raise credentials_exception
		token_data = TokenData(id=user_id, username=username)
	except JWTError as exception:
		raise credentials_exception from exception
	user = session.get(Users, token_data.id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	session.expire_on_commit = False
	return user

def authenticate_user(username: str, password: str):
	with get_session() as session:
		statement = select(Users).where(Users.username == username)
		user = session.exec(statement).first()
		if not user:
			return False
		if not verify_password(password, user.password):
			return False
		return user

@router.post("/token", response_model=Token)
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
	user = authenticate_user(login_form.username, login_form.password)
	if not user:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
	)
	return {"access_token": access_token, "token_type": "bearer"}

@router.get("", response_model=List[UserRead])
async def get_users(_: str = Depends(oauth2_scheme)):
	with get_session() as session:
		users = session.exec(select(Users)).all()
		return users


@router.get("/me", response_model=UserReadWithRelations)
async def get_me(current_user: UserRead = Depends(get_current_user)):
	return current_user


@router.get("/{user_id}", response_model=Union[UserReadWithRelations, None])
async def get_user(user_id: int, session: Session = Depends(get_session)):
	user = session.get(Users, user_id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(input_user: UserCreate):
	with get_session() as session:
		user = Users.from_orm(input_user)
		user.password = get_password_hash(user.password)
		session.add(user)
		session.commit()
		session.refresh(user)
		return user


@router.post("/{user_id}", response_model=UserRead)
async def update_user(input_user: UserUpdate, user_id: int):
	with get_session() as session:
		user = session.get(Users, user_id)
		if not user:
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
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		session.delete(user)
		session.commit()
		return
