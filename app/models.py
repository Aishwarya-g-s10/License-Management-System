from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import EmailStr
from typing import List, Optional

class LicenseStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"

class LicenseType(Enum):
    TRIAL = "TRIAL"
    PERPETUAL = "PERPETUAL"
    SUBSCRIPTION = "SUBSCRIPTION"

class User(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory = datetime.utcnow)
    licenses: List["License"] = Relationship(back_populates="users")
    company: Optional[str] = Relationship(back_populates="users")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pname: str = Field(index=True, unique=True)
    description: str 
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)
    license: List["License"] = Relationship(back_populates="products")

class License(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key = "user.id")
    product_id: int = Field(foreign_key = "product.id")
    description: str
    created_at: datetime = Field(default=datetime.utcnow())
    expiry_time: datetime = Field(default = datetime.utcnow())
    company_id: int = Field(foreign_key = "company.id")
    license_key: str
    status: LicenseStatus = Field(default = LicenseStatus.ACTIVE)
    license_type: LicenseType
    users: Optional["User"] = Relationship(back_populates="licenses")
    company_products: List["CompanyProduct"] = Relationship(back_populates="licenses")

class Company(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    company_name: str
    company_email: EmailStr
    users: List[User] = Relationship(back_populates="company")
    company_products: List["CompanyProduct"] = Relationship(back_populates="company")
    
class CompanyProduct(SQLModel, table=True):
    product_id: int = Field(foreign_key = "product.id", primary_key=True)
    company_id: int = Field(foreign_key = "company.id", primary_key=True)
    quantity: int = Field(default=1, ge=1)
    licenses: List[License] = Relationship(back_populates="company_products")
    products: List[Product] = Relationship(back_populates="products")

