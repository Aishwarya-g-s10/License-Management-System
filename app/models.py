from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"
    id:Optional[int] = Field(primary_key=True, default=None)
    username:str = Field(unique=True, index=True)
    email:EmailStr = Field(unique=True, index=True)
    password:str
    created_at:datetime = Field(default_factory=datetime.utcnow)

