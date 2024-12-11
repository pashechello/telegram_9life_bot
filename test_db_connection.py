import os
from sqlalchemy import create_engine

# Укажите данные для подключения к базе данных
DATABASE_URI = 'postgresql://catbot:ahfynbr5452@localhost:5432/mytelegrambot'

# Создание подключения к базе данных
engine = create_engine(DATABASE_URI)
connection = engine.connect()

# Проверка подключения
print("Connection successful!")

# Выполнение запроса для проверки работоспособности данных
try:
    result = connection.execute("SELECT 1")
    print("Query executed successfully:", result.fetchone())
except Exception as e:
    print("Error executing query:", e)

# Закрытие подключения
connection.close()