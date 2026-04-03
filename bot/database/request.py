from db import Base, Content
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)


async def reload_database() -> None:
    """
    Функция перезагрузки базы данных
    Сначала полностью удаляет её, а потом создаёт заново
    """
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)


async def insert_data(**kwargs):
    pass


async def update_data(id: int, **kwargs):
    pass


async def delete_data(id: int):
    pass
