from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, constr, conint
from sqlalchemy import Integer, ForeignKey, Table, Column, String, MetaData
metadata_obj = MetaData()

# Таблица для отделов
departments_table = Table(
    "departments",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String, unique=True, nullable=False),  # Название отдела
    Column('description', String, nullable=True)  # Описание отдела
)


# Таблица для результатов опросов
survey_results_table = Table(
    "survey_results",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('full_name', String, nullable=False),  # ФИО участника
    Column('department_id', Integer, ForeignKey('departments.id'), nullable=False),  # Внешний ключ к departments
    Column('year', Integer, nullable=False),  # Год проведения
    Column('month', Integer, nullable=False),  # Месяц проведения
    Column('health', Integer, nullable=False),  # Здоровье
    Column('love', Integer, nullable=False),  # Любовь
    Column('sex', Integer, nullable=False),  # Секс
    Column('work', Integer, nullable=False),  # Работа
    Column('rest', Integer, nullable=False),  # Отдых
    Column('money', Integer, nullable=False),  # Деньги
    Column('relationships', Integer, nullable=False),  # Отношения
    Column('personal_growth', Integer, nullable=False),  # Личностный рост
    Column('life_purpose', Integer, nullable=False),  # Смысл жизни
    Column('anxiety', Integer, nullable=False)  # Тревожность
)

class Department(BaseModel):
    name: str
    description: str | None = None
    
class SurveyResult(BaseModel):
    full_name: str
    department_id: int
    year: int
    month: int
    health: Annotated[int, Field(ge=0, le=10)]
    love: Annotated[int, Field(ge=0, le=10)]
    sex: Annotated[int, Field(ge=0, le=10)]
    work: Annotated[int, Field(ge=0, le=10)]
    rest: Annotated[int, Field(ge=0, le=10)]
    money: Annotated[int, Field(ge=0, le=10)]
    relationships: Annotated[int, Field(ge=0, le=10)]
    personal_growth: Annotated[int, Field(ge=0, le=10)]
    life_purpose: Annotated[int, Field(ge=0, le=10)]
    anxiety: Annotated[int, Field(ge=0, le=10)]