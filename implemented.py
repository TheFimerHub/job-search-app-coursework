import os
from dotenv import load_dotenv

# Загружает переменные окружения из файла .env и возвращает значение API_KEY.
load_dotenv()
api_key: str = os.getenv('API_KEY')
