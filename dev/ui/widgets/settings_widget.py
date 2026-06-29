from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QLineEdit, QSpinBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from database.connection import get_connection

class SettingsWidget(QWidget):
    back_signal = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("background-color: transparent;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)

        # Заголовок
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("BackButton")
        btn_back.setFixedWidth(120)
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        
        title = QLabel("⚙ Настройки")
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

        # Форма настроек
        form_container = QFrame()
        form_container.setObjectName("FormContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        user_name, daily_goal = self.main_window.get_user_data()

        # Имя
        name_layout = QHBoxLayout()
        name_label = QLabel("👤 Имя:")
        name_label.setStyleSheet("""
            font-size: 16px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.name_input = QLineEdit(user_name)
        self.name_input.setFixedHeight(45)
        self.name_input.setStyleSheet("""
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
        
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        # Дневная цель
        goal_layout = QHBoxLayout()
        goal_label = QLabel("🎯 Дневная цель (страниц):")
        goal_label.setStyleSheet("""
            font-size: 16px; 
            color: #AAAAAA;
            background-color: transparent;
            border: none;
        """)
        
        self.goal_input = QSpinBox()
        self.goal_input.setRange(1, 400)
        self.goal_input.setValue(daily_goal)
        self.goal_input.setFixedWidth(150)
        self.goal_input.setFixedHeight(45)
        self.goal_input.setStyleSheet("""
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
        
        goal_layout.addWidget(goal_label)
        goal_layout.addStretch()
        goal_layout.addWidget(self.goal_input)
        form_layout.addLayout(goal_layout)

        # Кнопка сохранения
        btn_save = QPushButton("💾 Сохранить настройки")
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedHeight(50)
        btn_save.clicked.connect(self.save_settings)
        form_layout.addWidget(btn_save)

        layout.addWidget(form_container)
        layout.addStretch()

    def save_settings(self):
        name = self.name_input.text().strip()
        goal = self.goal_input.value()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE user_profile SET name = ?, daily_goal = ? WHERE rowid = 1",
                (name, goal)
            )
            conn.commit()
            QMessageBox.information(self, "Успех", "Настройки сохранены!")
            
            # Обновляем daily_goal в main_window
            self.main_window.daily_goal = goal
            
            # ИСПРАВЛЕНО: вызываем update_tracker() без аргументов
            self.main_window.update_tracker()
            
            # Возвращаемся в библиотеку
            self.back_signal.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")
        finally:
            conn.close()