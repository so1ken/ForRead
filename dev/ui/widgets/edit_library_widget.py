from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

class EditBookCard(QFrame):
    edit_clicked = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)
    
    def __init__(self, book, controller):
        super().__init__()
        self.book = book
        self.controller = controller
        self.setObjectName("BookCard")
        self.setFixedSize(280, 120)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Мини обложка
        cover_label = QLabel()
        cover_label.setFixedSize(80, 100)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.book.cover_path:
            absolute_path = self.controller.get_absolute_path(self.book.cover_path)
            pixmap = QPixmap(absolute_path).scaled(
                80, 100,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            rounded = QPixmap(80, 100)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            clip_path = QPainterPath()
            clip_path.addRoundedRect(QRectF(0, 0, 80, 100), 8, 8)
            painter.setClipPath(clip_path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            cover_label.setPixmap(rounded)
        else:
            cover_label.setText("📚")
            cover_label.setStyleSheet("""
                font-size: 30px;
                background-color: #2A2A2A;
                border-radius: 8px;
            """)
        
        layout.addWidget(cover_label)

        # Информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        title_lbl = QLabel(self.book.title)
        title_lbl.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: #FFFFFF;
            background-color: transparent;
            border: none;
        """)
        title_lbl.setWordWrap(True)
        
        author_lbl = QLabel(self.book.author)
        author_lbl.setStyleSheet("""
            color: #AAAAAA;
            font-size: 13px;
            background-color: transparent;
            border: none;
        """)
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(author_lbl)
        info_layout.addStretch()
        
        layout.addLayout(info_layout, 1)

        # Кнопки
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        btn_edit = QPushButton("Изменить")
        btn_edit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A9EFF, stop:1 #00D4FF);
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5AAAFF, stop:1 #10E4FF);
            }
        """)
        btn_edit.setFixedHeight(35)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.book))
        
        btn_delete = QPushButton("Удалить")
        btn_delete.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF4444, stop:1 #FF6B6B);
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5555, stop:1 #FF7B7B);
            }
        """)
        btn_delete.setFixedHeight(35)
        btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.book))
        
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        
        layout.addLayout(btn_layout)


class EditLibraryWidget(QWidget):
    back_signal = pyqtSignal()
    edit_book_signal = pyqtSignal(object)
    book_deleted_signal = pyqtSignal()
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("background-color: transparent;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Заголовок
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("BackButton")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        
        title = QLabel("Редактировать библиотеку")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #FFFFFF;
            background-color: transparent;
            border: none;
        """)
        
        header_layout.addWidget(btn_back)
        header_layout.addStretch()
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addSpacing(120)
        
        layout.addLayout(header_layout)

        # Скролл с книгами
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #2A2A2A;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #4A4A4A;
                border-radius: 4px;
                min-height: 30px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)

        # Загружаем книги
        self.load_books()

    def load_books(self):
        # Очистка
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        books = self.controller.get_all_books()
        
        if not books:
            no_books_lbl = QLabel("Библиотека пуста")
            no_books_lbl.setStyleSheet("""
                font-size: 20px;
                color: #AAAAAA;
                background-color: transparent;
                border: none;
            """)
            no_books_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(no_books_lbl, 0, 0)
            return

        row, col = 0, 0
        max_cols = 2
        
        for book in books:
            card = EditBookCard(book, self.controller)
            card.edit_clicked.connect(self.on_edit_book)
            card.delete_clicked.connect(self.on_delete_book)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_edit_book(self, book):
        self.edit_book_signal.emit(book)

    def on_delete_book(self, book):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить книгу \"{book.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.delete_book(book.id):
                QMessageBox.information(self, "Успех", "Книга удалена!")
                self.book_deleted_signal.emit()
                self.load_books()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить книгу!")