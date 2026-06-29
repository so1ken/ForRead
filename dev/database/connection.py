import sqlite3
import os

# Получаем путь к папке, в которой лежит этот файл (database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Формируем полный путь к базе данных внутри папки database
DB_PATH = os.path.join(BASE_DIR, "books.db")

def get_connection():
    # Теперь мы подключаемся по абсолютному пути
    connection = sqlite3.connect(DB_PATH)
    return connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            pages_total INTEGER NOT NULL,
            pages_read INTEGER DEFAULT 0,
            review TEXT DEFAULT '',
            cover_path TEXT DEFAULT ''
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            daily_goal INTEGER DEFAULT 20,
            theme TEXT DEFAULT 'dark'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            pages_read INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()