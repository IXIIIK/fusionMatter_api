from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from dotenv import load_dotenv
from pydantic import BaseModel
import re
import requests
import os

app = FastAPI()

# CORS, если frontend на другом домене
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # укажи домен вместо * на проде
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# Телеграм токен и ID чата
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

class FormData(BaseModel):
    name: str
    email: str
    message: str


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Ошибка валидации данных"})


@app.post("/submit")
async def submit_form(data: FormData, request: Request):
    name = data.name.strip()
    email = data.email.strip()
    message = data.message.strip()

    # Простой анти-инжект и защита от скриптов
    dangerous_pattern = re.compile(r"[;\'\"--]|<script>|</script>", re.IGNORECASE)
    if any(dangerous_pattern.search(field) for field in [name, email, message]):
        raise HTTPException(status_code=400, detail="Недопустимые символы в форме.")

    # Формируем сообщение
    msg = f"📩 Новая заявка с сайта:\n\n👤 Имя: {name}\n📧 Контакт: {email}\n📝 Сообщение: {message}"

    # Отправка в Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    print("Отправляю в Telegram:", msg)
    print("URL:", url)
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

    if response.status_code != 200:
        print("Telegram error:", response.text)  # <— вот это покажет, что не так
        raise HTTPException(status_code=500, detail="Ошибка при отправке в Telegram")

    return {"status": "ok", "message": "Заявка успешно отправлена"}
