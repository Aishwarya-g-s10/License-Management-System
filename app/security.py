from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

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

