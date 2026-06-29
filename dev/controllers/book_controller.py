import sqlite3
import os
import shutil
import uuid
from pathlib import Path
from datetime import date
from models.book import Book
from database.connection import get_connection

class BookController:
    def __init__(self):
        # Определяем корень проекта и папку для обложек
        self.root_dir = Path(__file__).resolve().parent.parent
        self.covers_dir = self.root_dir / "data" / "covers"
        # Создаем папку, если она не существует
        self.covers_dir.mkdir(parents=True, exist_ok=True)

    def _save_cover_locally(self, original_path: str) -> str:
        """Копирует файл в data/covers и возвращает относительный путь"""
        if not original_path or not os.path.exists(original_path):
            return ""
        
        # Генерируем уникальное имя файла
        ext = Path(original_path).suffix
        new_filename = f"{uuid.uuid4()}{ext}"
        target_path = self.covers_dir / new_filename
        
        # Копируем файл
        shutil.copy2(original_path, target_path)
        
        # Возвращаем путь относительно корня (например: 'data/covers/xyz.jpg')
        return str(target_path.relative_to(self.root_dir)).replace("\\", "/")

    def _delete_cover(self, relative_path: str):
        """Удаляет файл, если он существует"""
        if not relative_path:
            return
        
        full_path = self.root_dir / relative_path
        if full_path.exists():
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Ошибка удаления файла: {e}")

    def get_absolute_path(self, relative_path: str) -> str:
        """Помогает UI найти полный путь к картинке для отображения"""
        if not relative_path:
            return ""
        return str(self.root_dir / relative_path)

    def add_book(self, title: str, author: str, pages_total: int, cover_path: str = "") -> bool:
        if len(title) != 0 and pages_total > 0:
            # Сохраняем обложку локально и получаем путь для БД
            local_cover_path = self._save_cover_locally(cover_path)
            
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, pages_total, cover_path) VALUES(?, ?, ?, ?)",
                (title, author, pages_total, local_cover_path)
            )
            connection.commit()
            connection.close()
            return True
        return False

    def update_book_cover(self, book_id: int, new_cover_path: str) -> bool:
        try:
            # Получаем старый путь из базы, чтобы удалить файл
            book = self.get_book_by_id(book_id)
            old_path = book.cover_path if book else ""
            
            # Сохраняем новую
            new_local_path = self._save_cover_locally(new_cover_path)
            
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE books SET cover_path = ? WHERE id = ?",
                (new_local_path, book_id)
            )
            connection.commit()
            connection.close()
            
            # Удаляем старый файл после успешного обновления БД
            self._delete_cover(old_path)
            return True
        except Exception as e:
            print(f"Ошибка обновления: {e}")
            return False

    def get_all_books(self) -> list:
        connection = get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT id, title, author, pages_total, pages_read, review, cover_path FROM books')
        rows = cursor.fetchall()
        books = []
        for row in rows:
            books.append(Book(
                row['id'], row['title'], row['author'], 
                row['pages_total'], row['pages_read'], 
                row['review'], row['cover_path']
            ))
        connection.close()
        return books
    
    def delete_book(self, book_id: int) -> bool:
        try:
            book = self.get_book_by_id(book_id)
            
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            connection.commit()
            connection.close()
            
            # Удаляем файл обложки
            if book and book.cover_path:
                self._delete_cover(book.cover_path)
            return True
        except Exception:
            return False

    def get_book_by_id(self, book_id: int) -> Book | None:
        connection = get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            'SELECT id, title, author, pages_total, pages_read, review, cover_path FROM books WHERE id = ?',
            (book_id,)
        )
        row = cursor.fetchone()
        connection.close()
        if row:
            return Book(
                row['id'],
                row['title'],
                row['author'],
                row['pages_total'],
                row['pages_read'],
                row['review'],
                row['cover_path']
            )
        return None

    def update_book(self, book_id: int, title: str, author: str, pages_total: int) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE books SET title = ?, author = ?, pages_total = ? WHERE id = ?",
                (title, author, pages_total, book_id)
            )
            connection.commit()
            connection.close()
            return True
        except Exception:
            return False

    def update_book_cover(self, book_id: int, cover_path: str) -> bool:
        """Обновить обложку книги"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            # Мы убрали os.remove(), чтобы программа 
            # не удаляла твои личные файлы с ПК при смене обложки.
            
            cursor.execute(
                "UPDATE books SET cover_path = ? WHERE id = ?",
                (cover_path, book_id)
            )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка обновления обложки: {e}")
            return False

    def update_book_review(self, book_id: int, review: str) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE books SET review = ? WHERE id = ?",
                (review, book_id)
            )
            connection.commit()
            connection.close()
            return True
        except Exception:
            return False

    def get_books_count(self) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    def get_total_pages_read(self) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(pages_read) FROM books")
        result = cursor.fetchone()[0]
        connection.close()
        return result if result else 0

    def get_today_progress(self) -> int:
        today = date.today().isoformat()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT pages_read FROM daily_progress WHERE date = ?",
            (today,)
        )
        row = cursor.fetchone()
        connection.close()
        return row[0] if row else 0

    def add_to_today_progress(self, pages: int) -> bool:
        today = date.today().isoformat()
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT pages_read FROM daily_progress WHERE date = ?", (today,))
            row = cursor.fetchone()
            if row:
                new_total = row[0] + pages
                cursor.execute(
                    "UPDATE daily_progress SET pages_read = ? WHERE date = ?",
                    (new_total, today)
                )
            else:
                cursor.execute(
                    "INSERT INTO daily_progress (date, pages_read) VALUES (?, ?)",
                    (today, pages)
                )
            connection.commit()
            return True
        except Exception:
            return False
        finally:
            connection.close()