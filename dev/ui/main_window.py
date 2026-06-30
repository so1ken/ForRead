import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QLabel, QPushButton, QGridLayout, 
    QScrollArea, QStackedWidget, QProgressBar,
    QSizeGrip
)
from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPainterPath, QIcon

from ui.widgets.book_card import BookCard
from ui.widgets.add_book_widget import AddBookWidget
from ui.widgets.reading_widget import ReadingWidget
from ui.widgets.settings_widget import SettingsWidget
from ui.widgets.edit_library_widget import EditLibraryWidget
from ui.widgets.edit_book_widget import EditBookWidget

from controllers.book_controller import BookController
from database.connection import get_connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ForRead")
        self.default_size = QSize(1200, 750)
        self.resize(self.default_size)
        self.setMinimumSize(800, 600)
        self.controller = BookController()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "assets", "icon.png")

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if icon.isNull():
                print(f"Иконка не загрузилась: {icon_path}")
            else:
                print(f"Иконка загружена: {icon_path}")
                self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Файл иконки не найден: {icon_path}")
            
        self.setup_ui()
        self.load_books()
        

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 2. Основная часть (Сайдбар + Контент)
        content_widget = QWidget()
        content_widget.setObjectName("ContentWidget")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)

        self.main_stack = QStackedWidget()
        self.main_stack.setObjectName("MainStack")
        
        library_page = self.create_library_page()
        self.main_stack.addWidget(library_page)
        
        self.add_book_widget = AddBookWidget(self.controller)
        self.add_book_widget.back_signal.connect(self.go_to_library)
        self.add_book_widget.book_added_signal.connect(self.on_book_added)
        self.main_stack.addWidget(self.add_book_widget)

        self.settings_widget = SettingsWidget(self)
        self.settings_widget.back_signal.connect(self.go_to_library)
        self.main_stack.addWidget(self.settings_widget)
        
        content_layout.addWidget(self.main_stack, 1)
        main_layout.addWidget(content_widget, 1)

        # 3. Нативный инструмент изменения размера (в правом нижнем углу)
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(15, 15)
        self.size_grip.setStyleSheet("background-color: transparent;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Динамически перемещаем SizeGrip в нижний правый угол при ресайзе
        self.size_grip.move(self.width() - 15, self.height() - 15)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(70)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)

        user_name, daily_goal = self.get_user_data()
        self.daily_goal = daily_goal

        first_letter = user_name[0].upper() if user_name else "?"
        profile_btn = QPushButton()
        profile_btn.setFixedSize(50, 50)
        profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        avatar = QPixmap(50, 50)
        avatar.fill(Qt.GlobalColor.transparent)
        painter = QPainter(avatar)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, 50, 50))
        painter.setClipPath(path)
        painter.fillRect(0, 0, 50, 50, QColor("#4A9EFF"))
        painter.end()
        
        from PyQt6.QtGui import QFont
        painter = QPainter(avatar)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(avatar.rect(), Qt.AlignmentFlag.AlignCenter, first_letter)
        painter.end()
        
        profile_btn.setStyleSheet("""
            QPushButton { border: none; border-radius: 25px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        profile_btn.setIcon(QIcon(avatar))
        profile_btn.setIconSize(QSize(50, 50))
        
        sidebar_layout.addWidget(profile_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addStretch()

        btn_settings = QPushButton()
        btn_settings.setFixedSize(50, 50)
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setStyleSheet("""
            QPushButton { border: none; border-radius: 25px; font-size: 24px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        btn_settings.setText("⚙")
        btn_settings.clicked.connect(self.go_to_settings)
        
        sidebar_layout.addWidget(btn_settings, alignment=Qt.AlignmentFlag.AlignCenter)
        return sidebar

    def create_library_page(self):
        page = QWidget()
        page.setObjectName("LibraryPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(20)

        title_lbl = QLabel("Мои книги")
        title_lbl.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: #FFFFFF;
            background-color: transparent; border: none;
        """)
        layout.addWidget(title_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #2A2A2A; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #4A4A4A; border-radius: 4px; min-height: 30px; }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("background-color: transparent;")
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 15, 0, 15)
        bottom_layout.setSpacing(20)

        btn_add = QPushButton("+ Добавить книгу")
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A9EFF, stop:1 #00D4FF);
                border: none; border-radius: 25px; font-size: 16px; font-weight: bold; color: #FFFFFF; padding: 0 30px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5AAAFF, stop:1 #10E4FF); }
        """)
        btn_add.setFixedHeight(50)
        btn_add.setFixedWidth(220)
        btn_add.clicked.connect(self.go_to_add_book)
        bottom_layout.addWidget(btn_add)

        btn_edit = QPushButton("Редактировать")
        btn_edit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9C27B0, stop:1 #BA68C8);
                border: none; border-radius: 25px; font-size: 16px; font-weight: bold; color: #FFFFFF; padding: 0 30px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #AB47BC, stop:1 #CA88D8); }
        """)
        btn_edit.setFixedHeight(50)
        btn_edit.setFixedWidth(200)
        btn_edit.clicked.connect(self.go_to_edit_library)
        bottom_layout.addWidget(btn_edit)

        tracker_frame = QFrame()
        tracker_frame.setObjectName("TrackerFrame")
        tracker_layout = QVBoxLayout(tracker_frame)
        tracker_layout.setContentsMargins(25, 15, 25, 15)
        tracker_layout.setSpacing(10)
        
        tracker_label = QLabel("Сегодняшний прогресс")
        tracker_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #AAAAAA; border: none;")
        tracker_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(14)
        
        self.progress_text = QLabel("0 / 0 страниц (0%)")
        self.progress_text.setStyleSheet("font-size: 14px; color: #4A9EFF; font-weight: bold; border: none;")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tracker_layout.addWidget(tracker_label)
        tracker_layout.addWidget(self.progress_bar)
        tracker_layout.addWidget(self.progress_text)
        
        bottom_layout.addWidget(tracker_frame)
        bottom_layout.addStretch()
        layout.addWidget(bottom_panel)
        return page

    # --- НАВИГАЦИЯ И УПРАВЛЕНИЕ ПАМЯТЬЮ ---
    def go_to_add_book(self):
        self.main_stack.setCurrentIndex(1)

    def go_to_library(self):
        self.main_stack.setCurrentIndex(0)
        self.load_books()

    def go_to_settings(self):
        self.main_stack.setCurrentIndex(2)

    def go_to_reading(self, book):
        if hasattr(self, 'reading_widget') and self.reading_widget is not None:
            self.main_stack.removeWidget(self.reading_widget)
            self.reading_widget.deleteLater()

        self.reading_widget = ReadingWidget(book, self.controller)
        self.reading_widget.back_signal.connect(self.go_to_library)
        self.reading_widget.progress_saved_signal.connect(self.on_progress_saved)
        self.main_stack.addWidget(self.reading_widget)
        self.main_stack.setCurrentWidget(self.reading_widget)

    def go_to_edit_library(self):
        if hasattr(self, 'edit_library_widget') and self.edit_library_widget is not None:
            self.main_stack.removeWidget(self.edit_library_widget)
            self.edit_library_widget.deleteLater()

        self.edit_library_widget = EditLibraryWidget(self.controller)
        self.edit_library_widget.back_signal.connect(self.go_to_library)
        self.edit_library_widget.book_deleted_signal.connect(self.on_book_deleted)
        self.edit_library_widget.edit_book_signal.connect(self.open_edit_book_widget)
        
        self.main_stack.addWidget(self.edit_library_widget)
        self.main_stack.setCurrentWidget(self.edit_library_widget)

    def open_edit_book_widget(self, book):
        if hasattr(self, 'edit_book_widget') and self.edit_book_widget is not None:
            self.main_stack.removeWidget(self.edit_book_widget)
            self.edit_book_widget.deleteLater()
            
        self.edit_book_widget = EditBookWidget(book, self.controller)
        
        def on_back_from_edit():
            self.edit_library_widget.load_books()
            self.main_stack.setCurrentWidget(self.edit_library_widget)
            
        self.edit_book_widget.back_signal.connect(on_back_from_edit)
        self.edit_book_widget.book_edited_signal.connect(self.on_book_edited)
        
        self.main_stack.addWidget(self.edit_book_widget)
        self.main_stack.setCurrentWidget(self.edit_book_widget)

    # --- ДАННЫЕ И СИГНАЛЫ ---
    def on_book_added(self):
        self.load_books()
        self.go_to_library()

    def on_book_deleted(self):
        self.load_books()

    def on_book_edited(self):
        self.load_books()

    def on_progress_saved(self, pages_read):
        self.update_tracker()

    def get_user_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name, daily_goal FROM user_profile LIMIT 1")
            row = cursor.fetchone()
        except:
            row = None
        conn.close()
        if row:
            return row[0], row[1]
        return "Читатель", 20

    def update_tracker(self):
        pages_read_today = self.controller.get_today_progress()
        percentage = min(int((pages_read_today / self.daily_goal) * 100), 100)
        
        self.progress_bar.setValue(percentage)
        self.progress_text.setText(f"{pages_read_today} / {self.daily_goal} страниц ({percentage}%)")
        
        if percentage >= 100:
            self.progress_bar.setStyleSheet("""
                QProgressBar { background-color: #2A2A2A; border-radius: 7px; }
                QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C853, stop:1 #69F0AE); border-radius: 7px; }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar { background-color: #2A2A2A; border-radius: 7px; }
                QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A9EFF, stop:1 #00D4FF); border-radius: 7px; }
            """)

    def load_books(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        books = self.controller.get_all_books()
        row, col = 0, 0
        max_cols = 4
        
        for book in books:
            card = BookCard(book, self.controller)
            card.book_clicked.connect(self.go_to_reading)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.grid_layout.setRowStretch(row + 1, 1)
        self.update_tracker()