import os

from dotenv import load_dotenv
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .db import Base, Content

load_dotenv()

user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "postgres")
db_name = os.getenv("DB_NAME", "umirhack_db")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Validate environment variables
if not all([user, password, db_name, db_host, db_port]):
    raise ValueError(
        "Missing database configuration. Please check your .env file.\n"
        f"DB_USER: {'✓' if user else '✗ MISSING'}\n"
        f"DB_PASSWORD: {'✓' if password else '✗ MISSING'}\n"
        f"DB_NAME: {'✓' if db_name else '✗ MISSING'}\n"
        f"DB_HOST: {'✓' if db_host else '✗ MISSING'}\n"
        f"DB_PORT: {'✓' if db_port else '✗ MISSING'}"
    )

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


async def insert_data(**kwargs):
    pass


async def update_data(id: int, **kwargs):
    pass


async def delete_data(id: int):
    pass
