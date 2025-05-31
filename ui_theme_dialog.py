# ui_theme_dialog.py

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QColorDialog

from styles import get_base_theme

class ThemeDialog(QDialog):
    """A dialog for letting the user customize the application's theme colors."""
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Theme")
        self.layout = QVBoxLayout(self)

        self.colors = {
            "primary_bg": "#2b2b2b", "secondary_bg": "#3c3f41",
            "text_color": "#bbbbbb", "accent_color": "#007acc",
            "button_bg": "#007acc", "button_text": "#ffffff"
        }

        self.color_buttons = {}
        for name, label in {
            "primary_bg": "Primary Background", "secondary_bg": "Secondary Background",
            "text_color": "Text Color", "accent_color": "Accent/Highlight",
            "button_bg": "Button Background", "button_text": "Button Text"
        }.items():
            btn = QPushButton(label)
            btn.clicked.connect(self.create_color_picker_lambda(name))
            self.layout.addWidget(btn)
            self.color_buttons[name] = btn

        self.update_button_styles()

    def create_color_picker_lambda(self, color_name):
        return lambda: self.pick_color(color_name)

    def pick_color(self, name):
        initial_color = QColor(self.colors[name])
        color = QColorDialog.getColor(initial_color, self, f"Select {name}")
        if color.isValid():
            self.colors[name] = color.name()
            self.update_button_styles()
            self.apply_theme()

    def apply_theme(self):
        stylesheet = get_base_theme(**self.colors)
        self.theme_changed.emit(stylesheet)

    def update_button_styles(self):
        for name, btn in self.color_buttons.items():
            q_color = QColor(self.colors[name])
            text_color = "#000000" if q_color.lightness() > 127 else "#ffffff"
            btn.setStyleSheet(f"background-color: {q_color.name()}; color: {text_color};")