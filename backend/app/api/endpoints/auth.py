from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Any
from pydantic import BaseModel
from app.core import security

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

# Mock user database
fake_users_db = {}

@router.post("/login", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = fake_users_db.get(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = security.create_access_token(subject=user["username"])
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=Token)
def register(user_in: UserCreate) -> Any:
    if user_in.username in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    fake_users_db[user_in.username] = {
        "username": user_in.username,
        "hashed_password": hashed_password
    }
    
    access_token = security.create_access_token(subject=user_in.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
