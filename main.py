# main.py

import sys
import os  # For path operations
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

from ui_settings_window import SettingsWindow
from styles import PREDEFINED_THEMES, get_base_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Robust font handling
    font_families = QFontDatabase.families()
    preferred_font = "JetBrains Mono"
    if preferred_font not in font_families:
        # Fallback fonts if JetBrains Mono is not available
        fallback_fonts = ["Consolas", "Courier New", "monospace"]
        for font_name in fallback_fonts:
            if font_name in font_families:
                preferred_font = font_name
                print(f"Warning: JetBrains Mono not found. Using fallback: {preferred_font}.")
                break
        else:  # If no fallbacks found, use system default
            preferred_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
            print(f"Warning: JetBrains Mono and fallbacks not found. Using system default: {preferred_font}.")

    app.setFont(QFont(preferred_font, 10))

    # Apply the default theme on startup
    default_theme_name = "Dark Blue (Default)"
    if default_theme_name in PREDEFINED_THEMES:
        colors = PREDEFINED_THEMES[default_theme_name]
        stylesheet = get_base_theme(**colors)
        app.setStyleSheet(stylesheet)
    else:
        print(f"Warning: Default theme '{default_theme_name}' not found in presets.")

    # Get the absolute path to this main.py script for the registry handler
    # This ensures the context menu correctly calls this script.
    main_script_path = os.path.abspath(__file__)

    window = SettingsWindow(main_script_path=main_script_path)
    window.show()
    sys.exit(app.exec())