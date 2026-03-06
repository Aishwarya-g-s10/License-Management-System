from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from .database import get_session
from fastapi import HTTPException
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate Credentials", headers={"WWW-Authetication": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.email==email)
    result = await session.execute(statement)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="You are not authorized to perform this action")
    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRY_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRY_TIME"))

if not SECRET_KEY or not ALGORITHM or not ACCESS_TOKEN_EXPIRY_TIME:
    raise ValueError("Environment Variable not found")


def hash_password(plain_password):
    truncated_pwd = plain_password[:72]
    return pwd_context.hash(truncated_pwd)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expiry_time = datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRY_TIME)
    to_encode.update({"exp": expiry_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

