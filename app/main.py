from datetime import datetime
import json
import os
import random
from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from database.core import add_department_to_db, add_survey_result_to_db, delete_department_from_db, get_all_departments, get_available_years, get_average_results_by_all_departments_and_month,  get_average_results_by_department_and_month, get_average_results_for_all_departments_comparison, get_comparison_of_departments
from models.models import Department, SurveyResult
from decimal import Decimal
import random

def get_random_color():
    return f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


def convert_decimal_to_float(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


# Главная страница с ссылками
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    message = request.query_params.get("message", None)
    departments = await get_all_departments()  # Загрузка отделов из базы
    years = await get_available_years()        # Загрузка доступных годов из базы
    current_year = datetime.now().year         # Текущий год для отображения по умолчанию

    return templates.TemplateResponse("index.html", {
        "request": request,
        "departments": departments,
        "years": years,
        "current_year": current_year,
        "message": message,
    })
# Страница с формой для заполнения
@app.get("/survey_form", response_class=HTMLResponse)
async def survey_form(request: Request):
    departments = await get_all_departments()
    return templates.TemplateResponse("survey_form.html", {"request": request, "departments": departments})

# Эндпоинт для добавления нового отдела
@app.post("/departments/add")
async def add_department(department: Department):
    return await add_department_to_db(department)

@app.delete("/departments/delete")
async def delete_department(id: int):
    return await delete_department_from_db(id)

# Эндпоинт для добавления результатов опроса
@app.post("/survey_results/add")
async def add_results(
    full_name: str = Form(...),
    department_id: int = Form(...),
    health: int = Form(...),
    love: int = Form(...),
    sex: int = Form(...),
    work: int = Form(...),
    rest: int = Form(...),
    money: int = Form(...),
    relationships: int = Form(...),
    personal_growth: int = Form(...),
    life_purpose: int = Form(...),
    anxiety: int = Form(...),
):
    current_year = datetime.now().year
    current_month = datetime.now().month

    survey_result = SurveyResult(
        full_name=full_name,
        department_id=department_id,
        health=health,
        love=love,
        sex=sex,
        work=work,
        rest=rest,
        money=money,
        relationships=relationships,
        personal_growth=personal_growth,
        life_purpose=life_purpose,
        anxiety=anxiety,
        year=current_year,
        month=current_month,
    )

    try:
        await add_survey_result_to_db(survey_result)
        return RedirectResponse(url="/?message=Ваши%20данные%20успешно%20сохранены!", status_code=303)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate_random_survey_results")
async def generate_random_survey_results(
    department_id: int,
    year: int,
    month: int,
    entries: int = 1  # Количество записей, которые нужно создать
):
    for _ in range(entries):
        survey_result = SurveyResult(
            full_name=f"Random User {random.randint(1, 1000)}",  # Генерация случайного имени
            department_id=department_id,
            health=random.randint(0, 10),
            love=random.randint(0, 10),
            sex=random.randint(0, 10),
            work=random.randint(0, 10),
            rest=random.randint(0, 10),
            money=random.randint(0, 10),
            relationships=random.randint(0, 10),
            personal_growth=random.randint(0, 10),
            life_purpose=random.randint(0, 10),
            anxiety=random.randint(0, 10),
            year=year,
            month=month
        )

        await add_survey_result_to_db(survey_result)

    return {"message": f"{entries} random survey results added successfully for department {department_id}, year {year}, month {month}"}

@app.get("/balance_wheel")
async def balance_wheel(request: Request, department_id: int, year: int):
    # Получение данных из базы
    raw_results = await get_average_results_by_department_and_month(department_id, year)

    # Преобразование Decimal в float
    average_results = convert_decimal_to_float(raw_results)

    # Получение информации об отделе
    department = await get_all_departments()
    department_name = next((d["name"] for d in department if d["id"] == department_id), "Неизвестный отдел")

    return templates.TemplateResponse("balance_wheel.html", {
        "request": request,
        "average_results": average_results,
        "department_name": department_name,
        "year": year
    })

@app.post("/balance_wheel_preview")
async def balance_wheel_preview(request: Request):
    data = await request.json()

    # Преобразуем все данные в float (если они в Decimal)
    data = convert_decimal_to_float(data)

    # Возвращаем успешный ответ с данными
    return {"success": True, "data": data}

@app.get("/balance_wheel_preview_result")
async def balance_wheel_preview_result(request: Request, data: str):
    # Декодируем данные, переданные через URL
    data = json.loads(data)
    
    return templates.TemplateResponse("balance_wheel_preview.html", {
        "request": request,
        "data": data
    })




@app.get("/balance_wheel/all_departments", response_class=HTMLResponse)
async def balance_wheel_all_departments(request: Request, year: int):
    # Получаем данные для всех отделов в заданном году
    raw_results = await get_average_results_by_all_departments_and_month(year)

    # Преобразование Decimal в float
    average_results = convert_decimal_to_float(raw_results)

    return templates.TemplateResponse("balance_wheel.html", {
        "request": request,
        "average_results": average_results,
        "department_name": "Все отделы",
        "year": year
    })


# @app.get("/compare_departments", response_class=HTMLResponse)
# async def compare_departments(request: Request, year: int):
#     departments = await get_all_departments()  # Получаем список всех отделов
#     all_departments_data = []

#     # Маппинг английских параметров на русские для отображения
#     param_translation = {
#         "health": "Здоровье",
#         "love": "Любовь",
#         "sex": "Секс",
#         "work": "Работа",
#         "rest": "Отдых",
#         "money": "Деньги",
#         "relationships": "Отношения",
#         "personal_growth": "Личностный рост",
#         "life_purpose": "Цель в жизни",
#         "anxiety": "Тревожность"
#     }

#     # Получаем данные для всех отделов
#     for department in departments:
#         department_data = await get_average_results_by_department_and_month(department["id"], year)
        
#         # Создаем список месяцев для текущего отдела, заполняя пустыми значениями по умолчанию
#         monthly_results = []
#         for month_idx in range(12):
#             # Проверяем, есть ли данные для текущего месяца
#             month_data = next((data for data in department_data if data["month"] == month_idx + 1), None)
            
#             if month_data:
#                 # Если данные для месяца есть, добавляем их
#                 monthly_results.append(month_data)
#             else:
#                 # Если данных нет, добавляем пустые значения
#                 monthly_results.append({
#                     "health": 0,
#                     "love": 0,
#                     "sex": 0,
#                     "work": 0,
#                     "rest": 0,
#                     "money": 0,
#                     "relationships": 0,
#                     "personal_growth": 0,
#                     "life_purpose": 0,
#                     "anxiety": 0
#                 })

#         all_departments_data.append({
#             "department_name": department["name"],
#             "monthly_results": monthly_results
#         })

#     # Список месяцев (можно оставить все месяцы, но фильтровать только те, которые есть в данных)
#     months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
#     datasets = []

#     # Параметры для оси X (параметры на русском)
#     parameters = list(param_translation.values())

#     valid_months = []

#     # Обрабатываем данные по месяцам
#     for month_idx in range(12):
#         # Проверяем, есть ли данные хотя бы для одного отдела в этом месяце
#         if any(department_data["monthly_results"][month_idx]["health"] > 0 for department_data in all_departments_data):
#             valid_months.append(months[month_idx])  # Добавляем только месяцы с данными
#             month_data = {
#                 "label": months[month_idx],  # Название месяца
#                 "data": [],
#                 "borderColor": get_random_color(),
#                 "fill": False
#             }

#             # Заполняем данные для каждого отдела
#             for department_data in all_departments_data:
#                 month_result = department_data["monthly_results"][month_idx]
#                 month_data["data"].append({
#                     "department_name": department_data["department_name"],
#                     "values": [
#                         float(month_result["health"]),
#                         float(month_result["love"]),
#                         float(month_result["sex"]),
#                         float(month_result["work"]),
#                         float(month_result["rest"]),
#                         float(month_result["money"]),
#                         float(month_result["relationships"]),
#                         float(month_result["personal_growth"]),
#                         float(month_result["life_purpose"]),
#                         float(month_result["anxiety"]),
#                     ]
#                 })

#             datasets.append(month_data)

#     return templates.TemplateResponse("compare_departments.html", {
#         "request": request,
#         "year": year,
#         "months": valid_months,  # Передаем только те месяцы, для которых есть данные
#         "parameters": parameters,  # Параметры для оси X
#         "datasets": datasets  # Данные для графиков
#     })

@app.get("/compare_departments", response_class=HTMLResponse)
async def compare_departments(request: Request, year: int, department_id: int = None):
    departments = await get_all_departments()
    specific_department_data = []
    specific_department_name = ""
    
    if department_id:
        specific_department = next((dep for dep in departments if dep["id"] == department_id), None)
        if specific_department:
            specific_department_name = specific_department["name"]
            specific_department_data = await get_average_results_by_department_and_month(department_id, year)
            
            # Преобразуем Decimal в float
            specific_department_data = [
                {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items()}
                for data in specific_department_data
            ]
            print("specific_department_data:", specific_department_data)  # Отладка

    # Маппинг параметров
    parameter_mapping = {
        "health": "Здоровье",
        "love": "Любовь",
        "sex": "Секс",
        "work": "Работа",
        "rest": "Отдых",
        "money": "Деньги",
        "relationships": "Отношения",
        "personal_growth": "Личностный рост",
        "life_purpose": "Цель в жизни",
        "anxiety": "Тревожность"
    }

    # Преобразуем данные для графика
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    parameters = list(parameter_mapping.values())  # Русские названия параметров

    chart_data = {
        "labels": parameters,  # Параметры на горизонтальной оси
        "datasets": [
            {
                "label": months[data["month"] - 1] if data["month"] - 1 < len(months) else f"Месяц {data['month']}",
                "data": [data.get(eng_key, 0) for eng_key in parameter_mapping.keys()],  # Данные на основе английских ключей
                "borderColor": get_random_color(),  # Цвет линии
                "fill": False
            }
            for idx, data in enumerate(specific_department_data)
        ]
    }

    return templates.TemplateResponse("compare_departments.html", {
        "request": request,
        "year": year,
        "months": months,
        "parameters": parameters,
        "specific_department_name": specific_department_name,
        "chart_data": chart_data
    })
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Получаем порт из переменной окружения или используем 8000 по умолчанию
    uvicorn.run(app, host="0.0.0.0", port=port)
