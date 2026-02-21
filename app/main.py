from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from .models import User
from pydantic import EmailStr
from .database import get_session, create_db_and_tables
from .schema import UserIn, UserOut
from typing import List


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def home():
    return {
        "message": "This is license management System"
    }

@app.post("/create_user")
def create_user(username: str, email: EmailStr, password: str, session: Session = Depends(get_session)):
    user = User(username=username, email=email, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return{
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

@app.get("/users", response_model=List[UserOut])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.put("/update_user/{user_id}", response_model=UserOut)
def update_user(user_id:int, username:str, email: EmailStr, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User ID Not Found")
    user.username = username
    user.email = email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.delete("/delete_user")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Id Not Found")
    session.delete(user)
    session.commit()
    return {
        "id": user_id,
        "message": "User Deleted successfully"
    }

    


