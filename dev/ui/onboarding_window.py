from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QStackedWidget, 
    QWidget, QHBoxLayout, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from database.connection import get_connection

class OnboardingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ForRead")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(800, 650)
        self.current_step = 0
        self.total_steps = 3
        self._drag_pos = None
        self.setup_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() <= 50:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                border-radius: 30px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === КАСТОМНЫЙ ЗАГОЛОВОК ===
        header = QFrame()
        header.setStyleSheet("""
            background-color: transparent;
            border-top-left-radius: 30px;
            border-top-right-radius: 30px;
        """)
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        title_lbl = QLabel("ForRead")
        title_lbl.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #4A9EFF;
            background-color: transparent;
        """)
        title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        header_layout.addWidget(title_lbl)
        
        header_layout.addStretch()
        
        dev_lbl = QLabel("by so1ken")
        dev_lbl.setStyleSheet("""
            font-size: 13px;
            color: #666666;
            background-color: transparent;
        """)
        dev_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        header_layout.addWidget(dev_lbl)
        
        main_layout.addWidget(header)

        # === ОСНОВНОЙ КОНТЕНТ ===
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(60, 30, 60, 50)
        content_layout.setSpacing(0)

        self.onboarding_progress = QProgressBar()
        self.onboarding_progress.setRange(0, 100)
        self.onboarding_progress.setValue(0)
        self.onboarding_progress.setTextVisible(False)
        self.onboarding_progress.setFixedHeight(6)
        self.onboarding_progress.setStyleSheet("""
            QProgressBar {
                background-color: #2A2A2A;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A9EFF, stop:1 #00D4FF);
                border-radius: 3px;
            }
        """)
        content_layout.addWidget(self.onboarding_progress)
        content_layout.addSpacing(40)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: transparent;")
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget)

        # === СЛАЙДЫ ===
        page1 = self.create_slide(
            "Как к тебе обращаться?",
            self.create_name_input(),
            "Далее",
            lambda: self.next_slide(0)
        )
        self.stacked_widget.addWidget(page1)

        page2 = self.create_slide(
            "Сколько тебе лет?",
            self.create_age_input(),
            "Далее",
            lambda: self.next_slide(1)
        )
        self.stacked_widget.addWidget(page2)

        page3 = self.create_slide(
            "Сколько страниц хочешь читать в день?",
            self.create_goal_input(),
            "Начать",
            self.save_profile
        )
        self.stacked_widget.addWidget(page3)

        self.update_progress()

    def create_slide(self, title, input_widget, btn_text, btn_callback):
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(35)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: transparent;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setWordWrap(True)
        title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        btn_next = QPushButton(btn_text)
        btn_next.setFixedWidth(200)
        btn_next.setFixedHeight(50)
        btn_next.setObjectName("PrimaryButton")
        btn_next.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A9EFF, stop:1 #00D4FF);
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5AAAFF, stop:1 #10E4FF);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A8EEF, stop:1 #00C4EF);
            }
        """)
        btn_next.clicked.connect(btn_callback)
        
        layout.addWidget(title_lbl)
        layout.addSpacing(30)
        layout.addWidget(input_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(50)
        layout.addWidget(btn_next, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return page

    def create_name_input(self):
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введи имя...")
        self.name_input.setFixedWidth(400)
        self.name_input.setFixedHeight(55)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                border: 2px solid #2A2A2A;
                border-radius: 15px;
                padding: 0 25px;
                font-size: 20px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4A9EFF;
            }
            QLineEdit::placeholder {
                color: #555555;
            }
        """)
        return self.name_input

    def create_age_input(self):
        self.age_input = QSpinBox()
        self.age_input.setRange(5, 120)
        self.age_input.setValue(18)
        self.age_input.setFixedWidth(250)
        self.age_input.setFixedHeight(55)
        self.age_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.age_input.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                border: 2px solid #2A2A2A;
                border-radius: 15px;
                padding: 0 50px 0 20px;
                font-size: 20px;
                color: #FFFFFF;
                selection-background-color: #4A9EFF;
            }
            QSpinBox:focus {
                border: 2px solid #4A9EFF;
            }
            QSpinBox::up-button {
                width: 30px;
                height: 26px;
                border: none;
                background-color: transparent;
                border-radius: 0px;
                subcontrol-origin: border;
                subcontrol-position: top right;
                padding-right: 5px;
            }
            QSpinBox::up-button:hover {
                background-color: #2A2A2A;
                border-top-right-radius: 13px;
            }
            QSpinBox::up-button:pressed {
                background-color: #3A3A3A;
            }
            QSpinBox::up-arrow {
                width: 10px;
                height: 10px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
            QSpinBox::down-button {
                width: 30px;
                height: 26px;
                border: none;
                background-color: transparent;
                border-radius: 0px;
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                padding-right: 5px;
            }
            QSpinBox::down-button:hover {
                background-color: #2A2A2A;
                border-bottom-right-radius: 13px;
            }
            QSpinBox::down-button:pressed {
                background-color: #3A3A3A;
            }
            QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
        """)
        return self.age_input

    def create_goal_input(self):
        self.goal_input = QSpinBox()
        self.goal_input.setSuffix(" страниц")
        self.goal_input.setRange(1, 400)
        self.goal_input.setValue(20)
        self.goal_input.setFixedWidth(320)
        self.goal_input.setFixedHeight(55)
        self.goal_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.goal_input.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E1E;
                border: 2px solid #2A2A2A;
                border-radius: 15px;
                padding: 0 50px 0 20px;
                font-size: 20px;
                color: #FFFFFF;
                selection-background-color: #4A9EFF;
            }
            QSpinBox:focus {
                border: 2px solid #4A9EFF;
            }
            QSpinBox::up-button {
                width: 30px;
                height: 26px;
                border: none;
                background-color: transparent;
                border-radius: 0px;
                subcontrol-origin: border;
                subcontrol-position: top right;
                padding-right: 5px;
            }
            QSpinBox::up-button:hover {
                background-color: #2A2A2A;
                border-top-right-radius: 13px;
            }
            QSpinBox::up-button:pressed {
                background-color: #3A3A3A;
            }
            QSpinBox::up-arrow {
                width: 10px;
                height: 10px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
            QSpinBox::down-button {
                width: 30px;
                height: 26px;
                border: none;
                background-color: transparent;
                border-radius: 0px;
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                padding-right: 5px;
            }
            QSpinBox::down-button:hover {
                background-color: #2A2A2A;
                border-bottom-right-radius: 13px;
            }
            QSpinBox::down-button:pressed {
                background-color: #3A3A3A;
            }
            QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
                image: none;
                background-color: #4A9EFF;
                border-radius: 2px;
            }
        """)
        return self.goal_input

    def next_slide(self, current_index):
        if current_index == 0 and not self.name_input.text().strip():
            self.name_input.setStyleSheet("""
                QLineEdit {
                    background-color: #3A2A2A;
                    border: 2px solid #FF5252;
                    border-radius: 15px;
                    padding: 0 25px;
                    font-size: 20px;
                    color: #FFFFFF;
                }
            """)
            return
        
        self.current_step += 1
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_progress()

    def update_progress(self):
        progress = int((self.current_step / (self.total_steps - 1)) * 100)
        self.onboarding_progress.setValue(progress)

    def save_profile(self):
        name = self.name_input.text().strip()
        age = self.age_input.value()
        goal = self.goal_input.value()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_profile (name, age, daily_goal) VALUES (?, ?, ?)",
            (name, age, goal)
        )
        conn.commit()
        conn.close()
        self.accept()