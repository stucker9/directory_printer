# styles.py

PREDEFINED_THEMES = {
    "Dark Blue (Default)": {
        "primary_bg": "#2b2b2b", "secondary_bg": "#3c3f41",
        "text_color": "#bbbbbb", "accent_color": "#007acc",
        "button_bg": "#007acc", "button_text": "#ffffff"
    },
    "Light Solarized": {
        "primary_bg": "#fdf6e3", "secondary_bg": "#eee8d5",
        "text_color": "#657b83", "accent_color": "#268bd2",
        "button_bg": "#2aa198", "button_text": "#ffffff"
    },
    "Monokai Pro": {
        "primary_bg": "#2D2A2E", "secondary_bg": "#403E41",
        "text_color": "#FCFCFA", "accent_color": "#FF6188", # Pink
        "button_bg": "#A9DC76", "button_text": "#2D2A2E"  # Green button
    },
    "Nordic Night": {
        "primary_bg": "#2E3440", "secondary_bg": "#3B4252",
        "text_color": "#D8DEE9", "accent_color": "#88C0D0", # Bluish
        "button_bg": "#5E81AC", "button_text": "#ECEFF4"
    },
    "Forest Green": {
        "primary_bg": "#222d22", "secondary_bg": "#344e41",
        "text_color": "#dad7cd", "accent_color": "#a3b18a",
        "button_bg": "#588157", "button_text": "#ffffff"
    },
    "Crimson Dark": {
        "primary_bg": "#1e1e1e", "secondary_bg": "#2d2d2d",
        "text_color": "#d4d4d4", "accent_color": "#ce3c3c",
        "button_bg": "#9a2a2a", "button_text": "#ffffff"
    },
    "Oceanic Light": {
        "primary_bg": "#e0fbfc", "secondary_bg": "#c2dfe3",
        "text_color": "#0d1b2a", "accent_color": "#3d5a80",
        "button_bg": "#98c1d9", "button_text": "#0d1b2a"
    }
}

def get_base_theme(primary_bg, secondary_bg, text_color, accent_color, button_bg, button_text):
    """Generates a QSS theme string from a set of colors."""
    return f"""
    QWidget {{
        font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
        color: {text_color};
        background-color: {primary_bg};
        font-size: 10pt;
    }}
    QMainWindow, QDialog {{
        background-color: {primary_bg};
    }}
    QGroupBox {{
        background-color: {secondary_bg};
        border: 1px solid {accent_color};
        border-radius: 5px;
        margin-top: 1ex; /* space for title */
        padding: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 5px;
        background-color: {primary_bg}; /* Match window background for a cleaner look */
        border-radius: 3px;
    }}
    QCheckBox, QRadioButton {{
        spacing: 5px; /* Space between indicator and text */
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 15px;
        height: 15px;
        border: 1px solid {accent_color};
        border-radius: 3px;
        background-color: {primary_bg}; /* Default state background */
    }}
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border: 1px solid {text_color}; /* Lighter border on hover */
    }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {accent_color};
        border: 1px solid {accent_color};
    }}
    QCheckBox::indicator:checked:disabled, QRadioButton::indicator:checked:disabled {{
        background-color: #555;
    }}
    QPushButton {{
        background-color: {button_bg};
        color: {button_text};
        border: 1px solid {accent_color}; /* Use accent for border for consistency */
        padding: 8px 15px;
        border-radius: 5px;
        outline: none; /* Remove focus outline */
        min-height: 20px; /* Ensure buttons have a decent height */
    }}
    QPushButton:hover {{
        background-color: {accent_color};
        color: {primary_bg if QColor(accent_color).lightnessF() > 0.5 else "#ffffff"}; /* Adjust text for contrast */
        border: 1px solid {button_bg}; /* Invert border on hover */
    }}
    QPushButton:pressed {{
        background-color: {QColor(accent_color).darker(120).name()}; /* Slightly darker on press */
    }}
    QPushButton:disabled {{
        background-color: #444; /* Darker disabled state */
        color: #777;
        border: 1px solid #555;
    }}
    QProgressBar {{
        border: 1px solid {accent_color};
        border-radius: 5px;
        text-align: center;
        color: {text_color};
        background-color: {secondary_bg}; /* Background for the bar itself */
    }}
    QProgressBar::chunk {{
        background-color: {accent_color};
        border-radius: 5px; /* Should match QProgressBar's radius */
        margin: 1px; /* Small margin to make the chunk distinct */
    }}
    QScrollArea {{
        border: none; /* Cleaner look */
    }}
    QComboBox {{
        border: 1px solid {accent_color};
        border-radius: 3px;
        padding: 1px 18px 1px 3px;
        min-width: 6em;
        background-color: {secondary_bg};
    }}
    QComboBox:on {{ /* shift the text when the popup opens */
        padding-top: 3px;
        padding-left: 4px;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: {accent_color};
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }}
    QComboBox::down-arrow {{
        /* image: url(path/to/your/arrow.png); Using a unicode arrow for simplicity */
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {accent_color};
        background-color: {secondary_bg};
        color: {text_color};
        selection-background-color: {accent_color};
    }}
    """
# Helper for QSS, since QColor is a Qt class
from PyQt6.QtGui import QColor