from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QPushButton, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

class ReadingWidget(QWidget):
    back_signal = pyqtSignal()
    progress_saved_signal = pyqtSignal(int)
    
    def __init__(self, book, controller):
        super().__init__()
        self.book = book
        self.controller = controller
        self.setStyleSheet("background-color: #1A1A1A;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Заголовок с кнопкой назад
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("BackButton")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        
        title = QLabel(f"📖 {self.book.title}")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #FFFFFF;
            background-color: transparent;
        """)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        header_layout.addWidget(btn_back)
        header_layout.addStretch()
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch()
        header_layout.addSpacing(120)
        
        layout.addLayout(header_layout)

        # Основная форма - ВСЕ УГЛЫ СКРУГЛЕННЫЕ
        form_container = QFrame()
        form_container.setObjectName("FormContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # Обложка книги - ИСПРАВЛЕНО: используем KeepAspectRatioByExpanding
        cover_label = QLabel()
        cover_label.setFixedSize(160, 220)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        if self.book.cover_path:
            path = self.controller.get_absolute_path(self.book.cover_path)
            pixmap = QPixmap(path).scaled(
                160, 220,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # ИЗМЕНЕНО
                Qt.TransformationMode.SmoothTransformation
            )
            rounded = QPixmap(160, 220)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, 160, 220), 12, 12)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            cover_label.setPixmap(rounded)
        else:
            cover_label.setText("")
            cover_label.setStyleSheet("""
                font-size: 60px; 
                background-color: #2A2A2A; 
                border-radius: 12px;
            """)
        
        form_layout.addWidget(cover_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Название и автор
        title_lbl = QLabel(self.book.title)
        title_lbl.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #FFFFFF;
            background-color: transparent;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        form_layout.addWidget(title_lbl)

        author_lbl = QLabel(self.book.author)
        author_lbl.setStyleSheet("""
            font-size: 14px; 
            color: #AAAAAA;
            background-color: transparent;
        """)
        author_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        form_layout.addWidget(author_lbl)

        # Прогресс
        progress_frame = QFrame()
        progress_frame.setObjectName("TrackerFrame")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 15, 20, 15)
        progress_layout.setSpacing(12)
        
        self.progress_info = QLabel(f"Прочитано: {self.book.pages_read} / {self.book.pages_total} страниц")
        self.progress_info.setStyleSheet("""
            font-size: 15px; 
            color: #AAAAAA;
            background-color: transparent;
        """)
        self.progress_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_info.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.book.pages_total)
        self.progress_bar.setValue(self.book.pages_read)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setObjectName("TrackerProgress")
        
        progress_layout.addWidget(self.progress_info)
        progress_layout.addWidget(self.progress_bar)
        form_layout.addWidget(progress_frame)

        # Ввод прочитанных страниц
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: transparent;")
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(12)
        
        input_label = QLabel("Сколько страниц прочитал сейчас?")
        input_label.setStyleSheet("""
            font-size: 15px; 
            color: #FFFFFF; 
            font-weight: bold;
            background-color: transparent;
        """)
        input_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        self.pages_input = QSpinBox()
        max_pages = max(1, self.book.pages_total - self.book.pages_read)
        self.pages_input.setRange(1, max_pages)
        self.pages_input.setValue(min(10, max_pages))
        self.pages_input.setFixedWidth(180)
        self.pages_input.setFixedHeight(45)
        self.pages_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pages_input.setStyleSheet("""
            QSpinBox {
                background-color: #2A2A2A;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 0 40px 0 15px;
                font-size: 16px;
                color: #FFFFFF;
            }
            QSpinBox:focus {
                border: 2px solid #4A9EFF;
                background-color: #2F2F2F;
            }
            QSpinBox::up-button {
                width: 25px;
                height: 21px;
                border: none;
                background-color: transparent;
                subcontrol-origin: border;
                subcontrol-position: top right;
                padding-right: 3px;
            }
            QSpinBox::up-button:hover {
                background-color: #3A3A3A;
                border-top-right-radius: 8px;
            }
            QSpinBox::up-arrow {
                width: 8px;
                height: 8px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
            QSpinBox::down-button {
                width: 25px;
                height: 21px;
                border: none;
                background-color: transparent;
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                padding-right: 3px;
            }
            QSpinBox::down-button:hover {
                background-color: #3A3A3A;
                border-bottom-right-radius: 8px;
            }
            QSpinBox::down-arrow {
                width: 8px;
                height: 8px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
        """)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.pages_input, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(input_frame)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setObjectName("SidebarButton")
        btn_cancel.setFixedHeight(45)
        btn_cancel.clicked.connect(lambda: self.back_signal.emit())
        
        btn_save = QPushButton("Сохранить прогресс")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedHeight(45)
        btn_save.clicked.connect(self.save_progress)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        form_layout.addLayout(btn_layout)

        layout.addWidget(form_container)
        layout.addStretch()

    def save_progress(self):
        pages_to_add = self.pages_input.value()
        new_pages_read = min(self.book.pages_read + pages_to_add, self.book.pages_total)
        
        if self.controller.update_book_pages(self.book.id, new_pages_read):
            # Добавляем к ежедневному прогрессу
            self.controller.add_to_today_progress(pages_to_add)
            
            self.book.pages_read = new_pages_read
            self.progress_bar.setValue(new_pages_read)
            self.progress_info.setText(f"Прочитано: {new_pages_read} / {self.book.pages_total} страниц")
            
            self.progress_saved_signal.emit(pages_to_add)