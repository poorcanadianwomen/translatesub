from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import pyqtSignal, QObject


class TraySignals(QObject):
    start = pyqtSignal()
    stop = pyqtSignal()
    quit = pyqtSignal()
    model_changed = pyqtSignal(str)


class TrayIcon:
    def __init__(self):
        self.signals = TraySignals()
        self._tray = QSystemTrayIcon()
        self._tray.setIcon(self._create_icon("TS"))
        self._tray.setToolTip("TranslateSub — Audio → Turkish")

        menu = QMenu()
        self._start_action = menu.addAction("▶  Start")
        self._start_action.triggered.connect(self.signals.start.emit)

        self._stop_action = menu.addAction("⏹  Stop")
        self._stop_action.triggered.connect(self.signals.stop.emit)
        self._stop_action.setEnabled(False)

        model_menu = menu.addMenu("STT Model")
        for model_name in ["base", "small", "medium", "large-v3"]:
            action = model_menu.addAction(model_name)
            action.setCheckable(True)
            if model_name == "base":
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=model_name: self._on_model_change(m))

        menu.addSeparator()
        quit_action = menu.addAction("✕  Exit")
        quit_action.triggered.connect(self.signals.quit.emit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_activate)

    def _create_icon(self, text):
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(50, 130, 200))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Sans", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), 0x0084, text)
        painter.end()
        return QIcon(pixmap)

    def _on_model_change(self, model_name):
        for action in self._tray.contextMenu().actions():
            if action.text() == "STT Model":
                for sub in action.menu().actions():
                    sub.setChecked(sub.text() == model_name)
        self.signals.model_changed.emit(model_name)

    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.signals.start.emit()

    def set_running(self, running):
        self._start_action.setEnabled(not running)
        self._stop_action.setEnabled(running)
        if running:
            self._tray.setIcon(self._create_icon("▶"))
            self._tray.setToolTip("TranslateSub — Running")
        else:
            self._tray.setIcon(self._create_icon("TS"))
            self._tray.setToolTip("TranslateSub — Stopped")

    def show(self):
        self._tray.show()

    def hide(self):
        self._tray.hide()

    def show_message(self, title, message):
        self._tray.showMessage(title, message)
