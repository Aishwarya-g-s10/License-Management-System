from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from pydantic import EmailStr
from .database import get_session, create_db_and_tables
from .schema import UserIn, UserOut
from typing import List
from .security import verify_password, create_access_token, hash_password


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
async def login(data: UserIn, session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.email == data.email)
    result = await session.execute(statement)
    user = result.scalars().first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/create_user", response_model=UserOut)
async def create_user(username: str, email: EmailStr, password: str, session: AsyncSession = Depends(get_session)):
    user = User(username=username, email=email, password=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@app.get("/get_users", response_model=List[UserOut])
async def get_users(session: AsyncSession = Depends(get_session)):
    users =  await session.execute(select(User))
    result = users.scalars().all()
    return result

@app.put("/update_user/{user_id}", response_model=UserOut)
async def update_user(user_id:int, username:str, email: EmailStr, session: AsyncSession = Depends(get_session)):
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
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Id Not Found")
    await session.delete(user)
    await session.commit()
    return {
        "id": user_id,
        "message": "User Deleted successfully"
    }

    


