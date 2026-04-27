from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Product, License
from pydantic import EmailStr
from .database import get_session, create_db_and_tables
from .schema import UserIn, UserOut, ProductOut, LicenseOut
from typing import List
from .security import verify_password, create_access_token, hash_password, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta



app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

@app.get("/")
def home():
    return {
        "message": "This is license management System"
    }

@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.email == data.username)
    result = await session.execute(statement)
    user = result.scalars().first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "Bearer"}


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# @app.post("/make_admin")
# async def make_admin(email: str,session: AsyncSession = Depends(get_session)):
#     result = await session.execute(select(User).where(User.email == email))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(404, "User not found")
#     user.is_admin = True
#     await session.commit()
#     return {"message": "User is now admin"}

@app.post("/create_user", response_model=UserOut)
async def create_user(username: str, email: EmailStr, password: str, session: AsyncSession = Depends(get_session)):
    user = User(username=username, email=email, password=hash_password(password))   
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@app.get("/get_users", response_model=List[UserOut])
async def get_users(session: AsyncSession = Depends(get_session), current_user: User = Depends(require_admin)):
    users =  await session.execute(select(User))
    result = users.scalars().all()
    return result

@app.put("/update_user/{user_id}", response_model=UserOut)
async def update_user(user_id:int, username:str, email: EmailStr, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You are unauthorized to perform this action")
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User ID Not Found")
    user.username = username
    user.email = email
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@app.delete("/delete_user")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_admin)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Id Not Found")
    try:
        await session.delete(user)
        await session.commit()
        return {
            "id": user_id,
            "message": "User Deleted successfully"
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database Error")

    
@app.post("/add_product", response_model=ProductOut)
async def add_product(name: str, description: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_admin)):
    sample = (await session.execute(select(Product).where(Product.pname==name))).scalars().first()
    if sample is not None:
        return {"message": "Product Name already Exists, try a different name"}
    product = Product(pname=name, description=description)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

@app.put("/update_product/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, product_name: str,product_description: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_admin)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product ID Not Found")
    product.pname = product_name
    product.description = product_description
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

@app.delete("/delete_product/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(require_admin)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product Id Not Found")
    try:
        samples = await session.execute(select(License).where(License.product_id==product_id))
        licenses = samples.scalars().all()
        for license in licenses:
            await session.delete(license)
        await session.delete(product)
        await session.commit()
        return {
            "id": product_id,
            "message": "Product Deleted successfully"
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database Error")

@app.get("/list_products", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = (await session.execute(select(Product))).scalars().all()
    return result

@app.post("/create_license", response_model=LicenseOut)
async def create_license(product_id: int, duration: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    expiry_date = datetime.now(timezone.utc) + timedelta(days=duration)
    new_license = License(expiry_date= expiry_date, user_id = current_user.id, product_id = product_id)
    session.add(new_license)
    await session.commit()
    await session.refresh(new_license)
    return new_license



@app.get("/get_license", response_model=list[LicenseOut])
async def list_licenses(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    result = (await session.execute(select(License))).scalars().all()
    return result

@app.post("/deactivate_license")
async def deactivate_license(license_key: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    sample = await session.execute(select(License).where(License.license_key==license_key, License.user_id==current_user.id))
    license = sample.scalars().first()
    if not license:
        raise HTTPException(status_code=404, detail="License Not found!")
    if not license.is_active:
        raise HTTPException(status_code=400, detail="License already deactivated")
    license.is_active = False
    license.deleted_at = datetime.utcnow()
    status = license.is_active
    await session.commit()
    return {
        "license_key": license_key,
        "status": status,
        "message": "Successfully deactivated license key"
    }
