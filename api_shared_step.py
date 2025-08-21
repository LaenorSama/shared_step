import requests
import os
# библиотека для загрузки данных из env
from dotenv import load_dotenv


# функция для получения bearer-токена нужного инстанса для токена администратора
def get_bearer_token(testops_api_url, testops_token):
    # URL для получения токена
    url = f"{testops_api_url}uaa/oauth/token"

    # Данные для запроса (в формате x-www-form-urlencoded)
    data = {
        "grant_type": "apitoken",
        "scope": "openid",
        "token": testops_token
    }

    # Заголовки
    headers = {
        "Accept": "application/json"
    }

    # Отправляем POST-запрос
    response = requests.post(url, data=data, headers=headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        try:
            token = response.json().get("access_token")
            if token:
                print("Bearer-токен получен")
                return token
            else:
                print("Ответ не содержит access_token:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ошибка парсинга JSON:", response.text)
    else:
        print("Ошибка получения токена:", response.status_code, response.text)

# функция получает название тест-кейса,
# возвращает переменную типа текст
def get_testcase_name(instance_name, testcase_id):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"  # Для корректной обработки JSON
    }
    response = requests.get(f"https://{instance_name}/api/testcase/{testcase_id}", headers=headers)
    scenario_data = response.json()
    # Извлекаем имя
    scenario_name = scenario_data["name"]
    print(f'Название тест-кейса: {scenario_name}')
    return scenario_name

# функция получается сценарий тест-кейса,
# возвращает список из шагов
def get_testcase_scenario(instance_name, testcase_id):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"  # Для корректной обработки JSON
    }
    response = requests.get(f"https://{instance_name}/api/testcase/{testcase_id}/step", headers=headers)
    scenario_data = response.json()
    # Извлекаем шаги
    children_ids = scenario_data["root"]["children"]
    steps = []

    for step_id in children_ids:
        step_data = scenario_data["scenarioSteps"].get(str(step_id))
        if step_data:
            steps.append(step_data["body"])

    # Выводим список шагов
    print('Получен сценарий:')
    for i, step in enumerate(steps, 1):
        print(f"Шаг {i}: {step}")

    return steps

# функция создает новый общий шаг,
# возвращает ID общего шага
def post_create_sharedstep(instance_name, project_id, sharedstep_name):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"  # Для корректной обработки JSON
    }
    # Формируем тело запроса
    payload = {
        "projectId": project_id,
        "name": sharedstep_name,
        "archived": False
    }
    response = requests.post(f"https://{instance_name}/api/sharedstep", headers=headers, json=payload)
    data = response.json()
    sharedstep_id = data["id"]
    print(f'Создан общий шаг. ID = {sharedstep_id}')
    return sharedstep_id

# функция добавляет в общий шаг сценарий из списка шагов,
# ничего не возвращает
def post_create_scenario_for_sharedstep(instance_name, sharedstep_id, testcase_scenario):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"  # Для корректной обработки JSON
    }
    print('Начинаем добавлять шаги сценария в общий шаг.')
    for step in testcase_scenario:
        # Формируем тело запроса
        payload = {
            "sharedStepId": sharedstep_id,
            "body": step
        }
        print(payload)
        response = requests.post(f"https://{instance_name}/api/sharedstep/step", headers=headers, json=payload)
        print(f'статус ответа: {response.status_code}')
        print(f'Добавлен шаг: {step}')
    return

# объявляем нужные переменные
PROJECT_ID = 282
TESTCASE_ID = 2234
INSTANCE_NAME = "demo.qatools.cloud"

# Загружаем .env файл
load_dotenv()
# Получаем токен из .env файла
TESTOPS_TOKEN = os.getenv("TESTOPS_TOKEN")
BEARER_TOKEN = get_bearer_token(f"https://{INSTANCE_NAME}/api/", TESTOPS_TOKEN)

# получаем имя тест-кейса
TESTCASE_NAME = get_testcase_name(INSTANCE_NAME, TESTCASE_ID)
# получаем сценарий тест-кейса
TESTCASE_SCENARIO = get_testcase_scenario(INSTANCE_NAME, TESTCASE_ID)
# создаем общий шаг
SHAREDSTEP_ID = post_create_sharedstep(INSTANCE_NAME, PROJECT_ID, TESTCASE_NAME)
# добавляем сценарий из списка шагов в общий шаг
post_create_scenario_for_sharedstep(INSTANCE_NAME, SHAREDSTEP_ID, TESTCASE_SCENARIO)


