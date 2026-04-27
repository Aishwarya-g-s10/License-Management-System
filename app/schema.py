from pydantic import EmailStr, BaseModel
from datetime import datetime

class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes=True

class ProductOut(BaseModel):
    id: int
    pname: str
    description: str
    class Config:
        from_attributes=True

class LicenseOut(BaseModel):
    id: int
    license_key: str
    product_id: int
    is_active: bool
    expiry_date: datetime
    class Config:
        from_attributes=True



