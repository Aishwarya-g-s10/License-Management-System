from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = "sqlite+aiosqlite:///./license.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread":False})

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

