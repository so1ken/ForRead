from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QSpinBox, QPushButton, QFileDialog,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

class AddBookWidget(QWidget):
    back_signal = pyqtSignal()
    book_added_signal = pyqtSignal()
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.cover_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(25)

        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("BackButton")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        
        title = QLabel("Добавить новую книгу")
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
        
        main_layout.addLayout(header_layout)

        form_container = QFrame()
        form_container.setObjectName("FormContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        self.title_input = self.create_input_field("Название книги")
        form_layout.addWidget(self.title_input)

        self.author_input = self.create_input_field("Автор")
        form_layout.addWidget(self.author_input)

        pages_layout = QHBoxLayout()
        pages_label = QLabel("Количество страниц:")
        pages_label.setStyleSheet("""
            font-size: 15px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.pages_input = QSpinBox()
        self.pages_input.setRange(1, 5000)
        self.pages_input.setValue(100)
        self.pages_input.setFixedWidth(200)
        self.pages_input.setStyleSheet("""
            QSpinBox {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 15px;
                color: #FFFFFF;
            }
            QSpinBox:focus {
                border: 2px solid #4A9EFF;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 30px;
                border: none;
                background: #3A3A3A;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #4A9EFF;
            }
        """)
        
        pages_layout.addWidget(pages_label)
        pages_layout.addStretch()
        pages_layout.addWidget(self.pages_input)
        form_layout.addLayout(pages_layout)

        cover_frame = QFrame()
        cover_frame.setStyleSheet("background-color: transparent;")
        cover_layout = QVBoxLayout(cover_frame)
        cover_layout.setSpacing(15)
        
        self.cover_preview = QLabel()
        self.cover_preview.setFixedSize(160, 220)  # Как в reading_widget
        self.cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_cover = QPushButton("Выбрать обложку")
        self.btn_cover.setObjectName("PrimaryButton")
        self.btn_cover.setFixedHeight(45)
        self.btn_cover.clicked.connect(self.select_cover)
        
        cover_layout.addWidget(self.cover_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        cover_layout.addWidget(self.btn_cover, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form_layout.addWidget(cover_frame)

        self.btn_save = QPushButton("Добавить книгу")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setFixedHeight(55)
        self.btn_save.clicked.connect(self.save_book)
        form_layout.addWidget(self.btn_save)

        main_layout.addWidget(form_container)
        main_layout.addStretch()

    def create_input_field(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(50)
        input_field.setStyleSheet("""
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
                background-color: #2F2F2F;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        return input_field

    def select_cover(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выбрать обложку", "", 
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_name:
            self.cover_path = file_name
            
            # Как в reading_widget - KeepAspectRatioByExpanding
            pixmap = QPixmap(file_name).scaled(
                160, 220,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Фиксированный размер как в reading_widget
            rounded = QPixmap(160, 220)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, 160, 220), 12, 12)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            self.cover_preview.setPixmap(rounded)
            self.btn_cover.setText("Обложка выбрана")

    def save_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        pages = self.pages_input.value()
        
        if not title:
            self.title_input.setStyleSheet("""
                QLineEdit {
                    background-color: #3A2A2A;
                    border: 2px solid #FF5252;
                    border-radius: 10px;
                    padding: 0 20px;
                    font-size: 15px;
                    color: #FFFFFF;
                }
            """)
            return
        
        self.controller.add_book(title, author, pages, self.cover_path)
        self.book_added_signal.emit()
        self.clear_form()

    def clear_form(self):
        self.title_input.clear()
        self.author_input.clear()
        self.pages_input.setValue(100)
        self.cover_path = ""
        self.cover_preview.clear()
        self.btn_cover.setText("Выбрать обложку")