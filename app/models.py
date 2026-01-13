from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Emailstr

class LicenseStatus(Enum):
    active = "ACTIVE"
    expired = "EXPIRED"

class LicenseType(Enum):
    trial = "TRIAL"
    perpetual = "PERPETUAL"
    subscription = "SUBSCRIPTION"

class Users(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Emailstr = Field(unique=True)
    password: str = Field(max_length=15)
    created_at: datetime = Field(default = datetime.utcnow())

class Products(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pname: str = Field(index=True, unique=True)
    description: str 
    created_at: datetime = Field(defualt = datetime.utcnow())
    updated_at: datetime = Field(default = datetime.utcnow())

class License(SQLModel, table=True):
    uname: str = Field(foriegn_key = "Users.username")
    product_id: int = Field(foriegn_key = "Products.id")
    description: str
    created_at: datetime = Field(default=datetime.utcnow())
    expiry_time: datetime = Field(default = datetime.utcnow())
    company_id: int = Field(foriegn_key = "Comapny.id")
    license_key: str
    status: LicenseStatus = Field(default = LicenseStatus.active)
    license_type: LicenseType

class Company(SQLModel, table=True):
    id: int
    company_name: str
    company_email: Emailstr
    
class CompanyProduct(SQLModel, table=True):
    product_id: int = Field(foriegn_key = "Products.id", primary_key=True)
    company_id: int = Field(foriegn_key = "Company.id", primary_key=True)
    quantity: int = Field(default=1, ge=1)
