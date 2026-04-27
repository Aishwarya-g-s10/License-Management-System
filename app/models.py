from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4
from .database import create_db_and_tables
from sqlalchemy import Integer, Column, ForeignKey


class User(SQLModel, table=True):
    __tablename__ = "user"
    id:Optional[int] = Field(primary_key=True, default=None)
    username:str = Field(unique=True, index=True)
    email:EmailStr = Field(unique=True, index=True)
    password:str
    is_admin: bool = Field(default=False)
    created_at:datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    licenses: List["License"] = Relationship(back_populates="owner")

class License(SQLModel, table=True):
    __tablename__ = "license"
    id: Optional[int] = Field(primary_key=True, default=None)
    license_key: str = Field(
        default_factory = lambda: str(uuid4()),
        unique=True,
        index=True
    )
    expiry_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    deleted_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(
        sa_column = Column(
            Integer,
            ForeignKey("product.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    owner: Optional["User"] = Relationship(back_populates="licenses")
    product: Optional["Product"] = Relationship(back_populates="licenses")

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expiry_date and datetime.now(timezone.utc) > self.expiry_date:
            return False
        return True

class Product(SQLModel, table=True):
    __tablename__ = "product"
    id: Optional[int] = Field(primary_key=True, default=None)
    pname: str = Field(unique=True, index=True)
    description: str
    licenses: List["License"] = Relationship(back_populates="product")

# def __main__():
#     create_db_and_tables()