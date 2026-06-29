from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QSpinBox, QPushButton, QFileDialog,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QIcon

class EditBookWidget(QWidget):
    back_signal = pyqtSignal()
    book_edited_signal = pyqtSignal()
    
    def __init__(self, book, controller):
        super().__init__()
        self.book = book
        self.controller = controller
        self.cover_path = book.cover_path if book.cover_path else ""
        self.setStyleSheet("background-color: transparent;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("BackButton")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        
        title = QLabel("Редактировать книгу")
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

        form_container = QFrame()
        form_container.setObjectName("FormContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        cover_frame = QFrame()
        cover_frame.setStyleSheet("background-color: transparent;")
        cover_layout = QVBoxLayout(cover_frame)
        cover_layout.setSpacing(15)
        
        self.cover_preview = QLabel()
        self.cover_preview.setFixedSize(160, 220)  # Как в reading_widget
        self.cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.cover_path:
            self.load_cover_preview(self.cover_path)
        
        btn_cover = QPushButton("Изменить обложку")
        btn_cover.setObjectName("PrimaryButton")
        btn_cover.setFixedHeight(45)
        btn_cover.clicked.connect(self.select_cover)
        
        cover_layout.addWidget(self.cover_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        cover_layout.addWidget(btn_cover, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(cover_frame)

        title_layout = QHBoxLayout()
        title_label = QLabel("Название:")
        title_label.setStyleSheet("""
            font-size: 16px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.title_input = QLineEdit(self.book.title)
        self.title_input.setFixedHeight(45)
        self.title_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 15px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4A9EFF;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)

        author_layout = QHBoxLayout()
        author_label = QLabel("Автор:")
        author_label.setStyleSheet("""
            font-size: 16px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.author_input = QLineEdit(self.book.author)
        self.author_input.setFixedHeight(45)
        self.author_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 15px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4A9EFF;
            }
        """)
        
        author_layout.addWidget(author_label)
        author_layout.addStretch()
        author_layout.addWidget(self.author_input)
        form_layout.addLayout(author_layout)

        pages_layout = QHBoxLayout()
        pages_label = QLabel("Страниц:")
        pages_label.setStyleSheet("""
            font-size: 16px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.pages_input = QSpinBox()
        self.pages_input.setRange(1, 5000)
        self.pages_input.setValue(self.book.pages_total)
        self.pages_input.setFixedWidth(150)
        self.pages_input.setFixedHeight(45)
        self.pages_input.setStyleSheet("""
            QSpinBox {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 15px;
                color: #FFFFFF;
            }
            QSpinBox:focus {
                border: 2px solid #4A9EFF;
            }
        """)
        
        pages_layout.addWidget(pages_label)
        pages_layout.addStretch()
        pages_layout.addWidget(self.pages_input)
        form_layout.addLayout(pages_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_delete = QPushButton("Удалить книгу")
        btn_delete.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF4444, stop:1 #FF6B6B);
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5555, stop:1 #FF7B7B);
            }
        """)
        btn_delete.setFixedHeight(50)
        btn_delete.clicked.connect(self.delete_book)
        
        btn_save = QPushButton("Сохранить")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedHeight(50)
        btn_save.clicked.connect(self.save_book)
        
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        form_layout.addLayout(btn_layout)

        layout.addWidget(form_container)
        layout.addStretch()

    def load_cover_preview(self, path):
        absolute_path = self.controller.get_absolute_path(path)
        
        # Как в reading_widget - KeepAspectRatioByExpanding
        pixmap = QPixmap(absolute_path).scaled(
            160, 220,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Фиксированный размер как в reading_widget
        rounded = QPixmap(160, 220)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path_obj = QPainterPath()
        path_obj.addRoundedRect(QRectF(0, 0, 160, 220), 12, 12)
        painter.setClipPath(path_obj)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        self.cover_preview.setPixmap(rounded)

    def select_cover(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выбрать обложку", "", 
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_name:
            self.cover_path = file_name
            self.load_cover_preview(file_name)

    def save_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        pages = self.pages_input.value()
        
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        success = self.controller.update_book(self.book.id, title, author, pages)
        
        if self.cover_path and self.cover_path != self.book.cover_path:
            self.controller.update_book_cover(self.book.id, self.cover_path)
        
        if success:
            QMessageBox.information(self, "Успех", "Книга обновлена!")
            self.book_edited_signal.emit()
            self.back_signal.emit()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить изменения!")

    def delete_book(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены что хотите удалить книгу \"{self.book.title}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.delete_book(self.book.id):
                QMessageBox.information(self, "Успех", "Книга удалена!")
                self.book_edited_signal.emit()
                self.back_signal.emit()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить книгу!")