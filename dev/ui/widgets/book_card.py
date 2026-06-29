from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRectF, pyqtSignal

class BookCard(QFrame):
    book_clicked = pyqtSignal(object)
    
    def __init__(self, book, controller):
        super().__init__()
        self.book = book
        self.controller = controller
        self.setObjectName("BookCard")
        self.setFixedSize(220, 350)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.book_clicked.emit(self.book)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.cover_label = QLabel()
        self.cover_label.setObjectName("CoverLabel")
        self.cover_label.setFixedSize(190, 260)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        if self.book.cover_path:
            absolute_path = self.controller.get_absolute_path(self.book.cover_path)
            pixmap = QPixmap(absolute_path).scaled(
                190, 260, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            rounded = QPixmap(190, 260)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            clip_path = QPainterPath()
            clip_path.addRoundedRect(QRectF(0, 0, 190, 260), 12, 12)
            painter.setClipPath(clip_path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.cover_label.setPixmap(rounded)
        else:
            self.cover_label.setText("Нет обложки")
        
        layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel(self.book.title)
        title_lbl.setStyleSheet("""
            font-weight: bold; 
            font-size: 15px; 
            margin-top: 5px; 
            color: #FFFFFF;
            background-color: transparent;
        """)
        title_lbl.setWordWrap(True)
        title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        author_lbl = QLabel(self.book.author)
        author_lbl.setStyleSheet("""
            color: #AAAAAA; 
            font-size: 13px;
            background-color: transparent;
        """)
        author_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        layout.addWidget(title_lbl)
        layout.addWidget(author_lbl)

        self.progress = QProgressBar()
        self.progress.setMaximum(self.book.pages_total)
        self.progress.setValue(self.book.pages_read)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        layout.addWidget(self.progress)