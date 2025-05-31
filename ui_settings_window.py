# ui_settings_window.py

import sys
import os
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QFileDialog, QMessageBox, QScrollArea, QFormLayout, QRadioButton,
    QProgressBar, QComboBox, QLabel, QHBoxLayout, QSpinBox  # QSpinBox is new
)

# Import from our new modules
from worker import Worker
from file_operations import save_as_csv, save_as_html, save_as_json
import registry_handler
from styles import PREDEFINED_THEMES, get_base_theme


class SettingsWindow(QMainWindow):
    def __init__(self, main_script_path):
        super().__init__()
        self.main_script_path = main_script_path
        self.setWindowTitle("Directory Printer")
        self.setGeometry(100, 100, 600, 700)  # Increased height for new option
        self.thread = None
        self.worker = None

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)

        # --- Theme Selector ---
        theme_group = QGroupBox("Appearance Theme")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Select Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(PREDEFINED_THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self.apply_selected_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # --- Context Menu Toggle ---
        context_menu_group = QGroupBox("Windows Context Menu")
        context_menu_layout = QVBoxLayout()
        self.context_menu_toggle = QCheckBox("Add 'Print Directory Contents (Py)' to folder right-click menu")
        self.context_menu_toggle.setChecked(registry_handler.check_context_menu_key_exists())
        self.context_menu_toggle.setTristate(False)
        self.context_menu_toggle.stateChanged.connect(self.handle_context_menu_toggle)
        context_menu_layout.addWidget(self.context_menu_toggle)
        context_menu_group.setLayout(context_menu_layout)
        layout.addWidget(context_menu_group)

        # --- NEW: Scan Options Group ---
        scan_options_group = QGroupBox("Scan Options")
        scan_options_layout = QHBoxLayout()
        self.depth_limit_check = QCheckBox("Limit scan depth to:")
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(1, 100)
        self.depth_spinbox.setValue(3)
        self.depth_spinbox.setEnabled(False)  # Disabled by default
        self.depth_limit_check.toggled.connect(self.depth_spinbox.setEnabled)
        scan_options_layout.addWidget(self.depth_limit_check)
        scan_options_layout.addWidget(self.depth_spinbox)
        scan_options_layout.addStretch()  # Pushes widgets to the left
        scan_options_group.setLayout(scan_options_layout)
        layout.addWidget(scan_options_group)

        # --- Output Format Group ---
        output_group = QGroupBox("Output Format")
        output_layout = QVBoxLayout()
        self.csv_radio = QRadioButton("CSV (Comma Separated Values)")
        self.html_radio = QRadioButton("HTML (Web Page)")
        self.json_radio = QRadioButton("JSON (Structured Data)")
        self.csv_radio.setChecked(True)
        output_layout.addWidget(self.csv_radio);
        output_layout.addWidget(self.html_radio);
        output_layout.addWidget(self.json_radio)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # --- Metadata Columns Group ---
        metadata_group = QGroupBox("Metadata Columns to Include")
        metadata_layout = QFormLayout()
        self.metadata_checkboxes = {
            "File Name": QCheckBox("File/Folder Name"), "Path": QCheckBox("Full Path"),
            "Size": QCheckBox("Size (bytes)"), "Creation Time": QCheckBox("Creation Time"),
            "Modification Time": QCheckBox("Modification Time"), "Access Time": QCheckBox("Access Time"),
            "Type": QCheckBox("File Type / Extension"), "Owner": QCheckBox("Owner (Unix-like)"),
            "Permissions": QCheckBox("Permissions (Octal)"),
        }
        for checkbox in self.metadata_checkboxes.values():
            checkbox.setChecked(True)
            metadata_layout.addRow(checkbox)
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)

        # --- Action Buttons ---
        self.save_button = QPushButton("Process Directory and Save Output")
        self.save_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.save_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

    def apply_selected_theme(self, theme_name):
        if theme_name in PREDEFINED_THEMES:
            colors = PREDEFINED_THEMES[theme_name]
            stylesheet = get_base_theme(**colors)
            QApplication.instance().setStyleSheet(stylesheet)

    def handle_context_menu_toggle(self, state):
        is_checked = (state == Qt.CheckState.Checked.value)
        success, message = (registry_handler.add_context_menu_key(self.main_script_path) if is_checked
                            else registry_handler.remove_context_menu_key())
        if success:
            QMessageBox.information(self, "Registry Update", message)
        else:
            QMessageBox.warning(self, "Registry Update Failed", message)
            self.context_menu_toggle.blockSignals(True)
            self.context_menu_toggle.setChecked(not is_checked)
            self.context_menu_toggle.blockSignals(False)

    def get_selected_metadata(self):
        return [key for key, checkbox in self.metadata_checkboxes.items() if checkbox.isChecked()]

    def start_processing(self):
        target_directory = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(
            sys.argv[1]) else QFileDialog.getExistingDirectory(self, "Select Directory to Process")
        if not target_directory:
            QMessageBox.information(self, "No Directory", "No directory selected for processing.")
            return

        self.save_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Preparing to scan... %p%")

        # Get depth limit options from the UI
        limit_depth_enabled = self.depth_limit_check.isChecked()
        max_depth = self.depth_spinbox.value()

        self.thread = QThread()
        # Pass the new options to the Worker
        self.worker = Worker(
            directory=target_directory,
            metadata_cols=self.get_selected_metadata(),
            limit_depth_enabled=limit_depth_enabled,
            max_depth=max_depth
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.preparation_finished.connect(self.on_preparation_finished)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_preparation_finished(self, total_items):
        self.progress_bar.setMaximum(total_items)
        if total_items == 0:
            self.progress_bar.setFormat("No items to process.")
        else:
            self.progress_bar.setFormat(f"Processing %v of %m items... (%p%)")

    def on_processing_finished(self, file_data):
        self.progress_bar.setVisible(False)
        self.save_button.setEnabled(True)

        if not file_data:
            QMessageBox.warning(self, "No Data", "No files or folders were found with the current settings.")
            return

        output_format = "csv"
        if self.html_radio.isChecked(): output_format = "html"
        if self.json_radio.isChecked(): output_format = "json"

        selected_metadata = self.get_selected_metadata()
        processed_dir_name = os.path.basename(self.worker.directory if self.worker else "output")
        suggested_filename = f"{processed_dir_name}_listing.{output_format}"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Directory Listing", suggested_filename,
                                                   f"{output_format.upper()} Files (*.{output_format});;All Files (*)")
        if not save_path:
            QMessageBox.information(self, "Save Cancelled", "File saving was cancelled.")
            return

        try:
            if output_format == "csv":
                save_as_csv(save_path, file_data, selected_metadata)
            elif output_format == "html":
                save_as_html(save_path, file_data, selected_metadata)
            elif output_format == "json":
                save_as_json(save_path, file_data)
            QMessageBox.information(self, "Success", f"Directory listing saved successfully to:\n{save_path}")
        except Exception as e:
            self.on_processing_error(str(e))

    def on_processing_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("Error occurred.")
        QMessageBox.critical(self, "Processing Error", f"An error occurred during processing:\n{error_message}")
        self.save_button.setEnabled(True)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()