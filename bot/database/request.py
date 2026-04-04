import os

from dotenv import load_dotenv
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .db import Base, Content

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{db_host}:{db_port}/{db_name}"

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


async def insert_data(**kwargs) -> bool:
    """Функция добавления данных"""
    try:
        async with async_session() as session:
            stmt = insert(Content).values(**kwargs)

            stmt = stmt.on_conflict_do_nothing(index_elements=["title"])

            await session.execute(stmt)
            await session.commit()
            return True
    except Exception as e:
        print(f"Ошибка вставки: {e}")
        return False


async def update_data(id: int, **kwargs):
    pass


async def delete_data(id: int):
    pass


async def get_content_by_category(category: str) -> list:
    """Функция получения данных"""
    async with async_session() as session:
        content = await session.scalars(
            select(Content).where(Content.category == category).limit(10)
        )
        content_all = content.all()
        return list(content_all)


async def get_topics() -> list:
    async with async_session() as session:
        content = (
            await session.scalars(select(Content.category).distinct())
        ).all()  # уникальные
        return list(content)
