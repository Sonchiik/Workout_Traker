import os
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_active: bool
    is_admin: bool = False
    
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes={'bcrypt'}, deprecated='auto')


def create_access_token(username: str, user_id: int, is_admin: bool, expires_delta: timedelta):
    encode = {
        'sub': username,
        "user_id": user_id,
        "is_admin": is_admin
    }
    
    exp = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": exp})
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def user_authentification(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user
    
async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: bool = payload.get('user_id')
        is_admin: bool = payload.get('is_admin')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        return {"username": username, "user_id": user_id, "is_admin": is_admin}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
@router.post('/user', status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db: db_dependency):
    new_user = Users(
        username = user.username,
        hashed_password = bcrypt_context.hash(user.password),
        is_active = True,
        is_admin = user.is_admin
    )
    
    existing_user = db.query(Users).filter(Users.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post('/token', status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
     user = user_authentification(form_data.username, form_data.password, db)
     
     if not user:
         raise HTTPException(status_code=401, detail="Authentication failed")
     
     token = create_access_token(user.username, user.id, user.is_admin, expires_delta=timedelta(minutes=20))
     return {"access_token": token, "token_type": "bearer"}