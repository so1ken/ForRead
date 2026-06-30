import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon  # ДОБАВИТЬ

# Импортируем модули
import ui.main_window as ui_main
import ui.onboarding_window as ui_onboarding

# Импортируем логику бэкенда
from database.connection import create_tables, get_connection

def check_is_first_run():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM user_profile")
        count = cursor.fetchone()[0]
    except Exception:
        count = 0
    conn.close()
    return count == 0

def main():
    # Инициализация БД
    sys.stdout.reconfigure(encoding='utf-8')
    create_tables()

    app = QApplication(sys.argv)
    
    # Иконка
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Определяем путь к файлу стилей относительно этого файла (main.py)
    style_path = os.path.join(base_dir, "ui", "styles.qss")

    # Загрузка стилей
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Файл стилей не найден по пути: {style_path}")

    # Логика запуска: если профиля нет, показываем Onboarding
    if check_is_first_run():
        onboarding = ui_onboarding.OnboardingWindow()
        if onboarding.exec() == 0: 
            sys.exit()

    # Запуск основного окна
    window = ui_main.MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()