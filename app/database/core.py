from statistics import mean
from sqlalchemy import select, text
from database.database import async_engine
from models.models import Department, SurveyResult
from sqlalchemy.engine import Row
    
    
# Преобразуем Row в словарь
def row_to_dict(row: Row):
    return {column: row[column] for column in row.keys()}


# Функция добавления нового отдела
async def add_department_to_db(department: Department):
    async with async_engine.connect() as conn:
        stmt = '''INSERT INTO departments (name, description) VALUES (:name, :description)'''
        await conn.execute(text(stmt), {"name": department.name, "description": department.description})
        await conn.commit()
    return {"message": "Department added successfully"}

async def delete_department_from_db(department_id: int):
    # Убедимся, что отдел с таким ID существует
    async with async_engine.connect() as conn:
        # Начинаем транзакцию
        async with conn.begin():
            # Сначала удалим все связанные записи в таблице survey_results
            delete_survey_results_stmt = '''DELETE FROM survey_results WHERE department_id = :department_id'''
            await conn.execute(text(delete_survey_results_stmt), {"department_id": department_id})

            # Теперь удалим сам отдел из таблицы departments
            delete_department_stmt = '''DELETE FROM departments WHERE id = :department_id'''
            result = await conn.execute(text(delete_department_stmt), {"department_id": department_id})
            
            # Проверим, был ли удалён отдел
            if result.rowcount == 0:
                return {"message": "Department not found or already deleted."}

    return {"message": "Department deleted successfully"}

async def get_all_departments():
    async with async_engine.connect() as conn:
        stmt = '''SELECT id, name, description FROM departments'''
        result = await conn.execute(text(stmt))
        rows = result.fetchall()
    return [{"id": row.id, "name": row.name, "description": row.description} for row in rows]

# Функция добавления результатов опроса
async def add_survey_result_to_db(survey_result: SurveyResult):
    async with async_engine.connect() as conn:
        stmt = '''INSERT INTO survey_results 
                  (full_name, department_id, year, month, health, love, sex, work, rest, money, relationships, personal_growth, life_purpose, anxiety) 
                  VALUES (:full_name, :department_id, :year, :month, :health, :love, :sex, :work, :rest, :money, :relationships, :personal_growth, :life_purpose, :anxiety)'''
        await conn.execute(text(stmt), {
            "full_name": survey_result.full_name,
            "department_id": survey_result.department_id,
            "year": survey_result.year,
            "month": survey_result.month,
            "health": survey_result.health,
            "love": survey_result.love,
            "sex": survey_result.sex,
            "work": survey_result.work,
            "rest": survey_result.rest,
            "money": survey_result.money,
            "relationships": survey_result.relationships,
            "personal_growth": survey_result.personal_growth,
            "life_purpose": survey_result.life_purpose,
            "anxiety": survey_result.anxiety
        })
        await conn.commit()
    return {"message": "Survey result added successfully"}


async def get_average_results_by_all_departments_and_month(year: int):
    async with async_engine.connect() as conn:
        stmt = '''
        SELECT 
            month,
            AVG(health) AS health,
            AVG(love) AS love,
            AVG(sex) AS sex,
            AVG(work) AS work,
            AVG(rest) AS rest,
            AVG(money) AS money,
            AVG(relationships) AS relationships,
            AVG(personal_growth) AS personal_growth,
            AVG(life_purpose) AS life_purpose,
            AVG(anxiety) AS anxiety
        FROM survey_results
        WHERE year = :year
        GROUP BY month
        ORDER BY month
        '''
        result = await conn.execute(text(stmt), {"year": year})
        rows = result.fetchall()
    return [{"month": row.month,
             "health": row.health,
             "love": row.love,
             "sex": row.sex,
             "work": row.work,
             "rest": row.rest,
             "money": row.money,
             "relationships": row.relationships,
             "personal_growth": row.personal_growth,
             "life_purpose": row.life_purpose,
             "anxiety": row.anxiety} for row in rows]

# Функция для получения всех результатов опроса из базы данных
async def get_all_survey_results():
    async with async_engine.connect() as conn:
        stmt = '''SELECT health, love, sex, work, rest, money, relationships, personal_growth, life_purpose, anxiety 
                  FROM survey_results'''
        result = await conn.execute(text(stmt))
        rows = result.fetchall()
    return rows

async def get_available_years():
    async with async_engine.connect() as conn:
        stmt = '''SELECT DISTINCT year FROM survey_results ORDER BY year DESC'''
        result = await conn.execute(text(stmt)) 
        rows = result.fetchall()
    return [row.year for row in rows]

async def get_department_name(department_id: int):
    async with async_engine.connect() as conn:
        stmt = '''SELECT name FROM departments WHERE id = :department_id'''
        result = await conn.execute(text(stmt), {"department_id": department_id})
        row = result.fetchone()
    return {"name": row.name} if row else {"name": "Неизвестный отдел"}

# Функция для получения средних значений по показателям
async def get_average_results_by_department_and_month(department_id: int, year: int):
    async with async_engine.connect() as conn:
        stmt = '''
        SELECT 
            month,
            AVG(health) AS health,
            AVG(love) AS love,
            AVG(sex) AS sex,
            AVG(work) AS work,
            AVG(rest) AS rest,
            AVG(money) AS money,
            AVG(relationships) AS relationships,
            AVG(personal_growth) AS personal_growth,
            AVG(life_purpose) AS life_purpose,
            AVG(anxiety) AS anxiety
        FROM survey_results
        WHERE department_id = :department_id AND year = :year
        GROUP BY month
        ORDER BY month
        '''
        result = await conn.execute(text(stmt), {"department_id": department_id, "year": year})
        rows = result.fetchall()
    return [{"month": row.month,
             "health": row.health,
             "love": row.love,
             "sex": row.sex,
             "work": row.work,
             "rest": row.rest,
             "money": row.money,
             "relationships": row.relationships,
             "personal_growth": row.personal_growth,
             "life_purpose": row.life_purpose,
             "anxiety": row.anxiety} for row in rows]

async def get_average_results(department_id, year):
    async with async_engine.connect() as conn:
        stmt = text("""
            SELECT
                AVG(health) AS health,
                AVG(love) AS love,
                AVG(sex) AS sex,
                AVG(work) AS work,
                AVG(rest) AS rest,
                AVG(money) AS money,
                AVG(relationships) AS relationships,
                AVG(personal_growth) AS personal_growth,
                AVG(life_purpose) AS life_purpose,
                AVG(anxiety) AS anxiety
            FROM survey_results
            WHERE department_id = :department_id AND year = :year
        """)
        result = await conn.execute(stmt, {"department_id": department_id, "year": year})
        rows = result.fetchall()
    
    if rows:
        return [dict(row._mapping) for row in rows]
    else:
        return []




async def get_average_results_for_all_departments_comparison(year: int):
    async with async_engine.connect() as conn:
        stmt = '''
        SELECT 
            department_id,
            month,
            AVG(health) AS health,
            AVG(love) AS love,
            AVG(sex) AS sex,
            AVG(work) AS work,
            AVG(rest) AS rest,
            AVG(money) AS money,
            AVG(relationships) AS relationships,
            AVG(personal_growth) AS personal_growth,
            AVG(life_purpose) AS life_purpose,
            AVG(anxiety) AS anxiety
        FROM survey_results
        WHERE year = :year
        GROUP BY department_id, month
        ORDER BY month, department_id
        '''
        result = await conn.execute(text(stmt), {"year": year})
        rows = result.fetchall()
    
    return [
        {
            "department_id": row.department_id,
            "month": row.month,
            "health": row.health,
            "love": row.love,
            "sex": row.sex,
            "work": row.work,
            "rest": row.rest,
            "money": row.money,
            "relationships": row.relationships,
            "personal_growth": row.personal_growth,
            "life_purpose": row.life_purpose,
            "anxiety": row.anxiety
        }
        for row in rows
    ]

# Функция для получения сравнительных результатов всех отделов за год
async def get_comparison_of_departments(year: int):
    async with async_engine.connect() as conn:
        stmt = '''
        SELECT 
            department_id,
            month,
            AVG(health) AS health,
            AVG(love) AS love,
            AVG(sex) AS sex,
            AVG(work) AS work,
            AVG(rest) AS rest,
            AVG(money) AS money,
            AVG(relationships) AS relationships,
            AVG(personal_growth) AS personal_growth,
            AVG(life_purpose) AS life_purpose,
            AVG(anxiety) AS anxiety
        FROM survey_results
        WHERE year = :year
        GROUP BY department_id, month
        ORDER BY department_id, month
        '''
        result = await conn.execute(text(stmt), {"year": year})
        rows = result.fetchall()

    return [
        {
            "department_id": row.department_id,
            "month": row.month,
            "health": row.health,
            "love": row.love,
            "sex": row.sex,
            "work": row.work,
            "rest": row.rest,
            "money": row.money,
            "relationships": row.relationships,
            "personal_growth": row.personal_growth,
            "life_purpose": row.life_purpose,
            "anxiety": row.anxiety
        }
        for row in rows
    ]
