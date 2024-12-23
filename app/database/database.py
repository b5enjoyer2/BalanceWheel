import logging
from fastapi import HTTPException
from sqlalchemy import create_engine, text, URL
from sqlalchemy.ext.asyncio import create_async_engine
from database.config import settings
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://postgres:zHjzKWMYwhGAVnXSvvHetVIupyATWugo@autorack.proxy.rlwy.net:28393/railway"

sync_engine = create_engine(url=settings.DATABASE_URL_psycopg, echo=True, pool_size = 5, max_overflow = 10)
async_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=False, pool_size = 5, max_overflow = 10)

async def check_db_connection():
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Не удалось подключиться к базе данных.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Неизвестная ошибка базы данных.")