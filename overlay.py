import json
import os
from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSettings
from PyQt6.QtGui import QFont, QColor, QTextCursor

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".translatesub_overlay.json")


class OverlaySignals(QObject):
    update_text = pyqtSignal(str, str)


class SubtitleOverlay(QWidget):
    def __init__(self, max_lines=50, fade_ms=8000):
        super().__init__()
        self.max_lines = max_lines
        self.fade_ms = fade_ms
        self.signals = OverlaySignals()
        self.signals.update_text.connect(self._on_new_text)

        self._line_count = 0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setMinimumSize(300, 100)
        self.resize(500, 180)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text.setFont(QFont("Sans", 13, QFont.Weight.Bold))
        self._text.setStyleSheet(
            "QTextEdit {"
            "  color: white;"
            "  background-color: rgba(0, 0, 0, 180);"
            "  border: none;"
            "  border-radius: 10px;"
            "  padding: 10px 14px;"
            "  selection-background-color: rgba(100, 100, 255, 100);"
            "}"
            "QScrollBar:vertical {"
            "  width: 8px;"
            "  background: transparent;"
            "}"
            "QScrollBar::handle:vertical {"
            "  background: rgba(255, 255, 255, 60);"
            "  border-radius: 4px;"
            "  min-height: 20px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "  height: 0px;"
            "}"
        )
        layout.addWidget(self._text)
        self.setLayout(layout)

        self._load_geometry()
        self._fade_timer = QTimer()
        self._fade_timer.timeout.connect(self._tick)
        self._fade_timer.start(1000)

    def _on_new_text(self, text, username):
        if not text or text.startswith("["):
            return

        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(
            f'<span style="color: #6ec6ff;"><b>{username}:</b></span> '
            f'<span style="color: white;">{text}</span><br>'
        )
        self._line_count += 1

        if self._line_count > self.max_lines:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
            self._line_count -= 1

        scrollbar = self._text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        if not self.isVisible():
            self.show()

    def _tick(self):
        pass

    def moveEvent(self, event):
        super().moveEvent(event)
        self._save_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._save_geometry()

    def _save_geometry(self):
        try:
            data = {
                "x": self.x(),
                "y": self.y(),
                "w": self.width(),
                "h": self.height(),
            }
            with open(CONFIG_PATH, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _load_geometry(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH) as f:
                    data = json.load(f)
                self.move(data["x"], data["y"])
                self.resize(data["w"], data["h"])
                return
        except Exception:
            pass
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2 + geo.x()
            y = geo.height() - 200 + geo.y()
            self.move(x, y)

    def closeEvent(self, event):
        self._save_geometry()
        self._fade_timer.stop()
        super().closeEvent(event)
