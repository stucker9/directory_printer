# worker.py

import os
import sys
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

IS_WINDOWS = sys.platform == "win32"
if not IS_WINDOWS:
    try:
        import pwd
    except ImportError:
        print("Warning: 'pwd' module not found, file ownership cannot be determined.")
        IS_WINDOWS = True  # Treat as Windows for ownership purposes


class Worker(QObject):
    preparation_finished = pyqtSignal(int)
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, directory, metadata_cols, limit_depth_enabled, max_depth):
        super().__init__()
        self.directory = directory
        self.metadata_cols = metadata_cols
        self.is_running = True
        # Store the new depth limit options
        self.limit_depth_enabled = limit_depth_enabled
        self.max_depth = max_depth

    def run(self):
        try:
            total_items = 0
            # Normalize the starting path to correctly calculate depth
            start_path = self.directory.rstrip(os.sep)
            start_depth = start_path.count(os.sep)

            # First pass to count items, respecting the depth limit
            for root, dirs, files in os.walk(self.directory, onerror=lambda err: print(f"Access error: {err}")):
                # --- DEPTH LIMIT LOGIC ---
                current_depth = root.count(os.sep) - start_depth
                if self.limit_depth_enabled and current_depth >= self.max_depth:
                    # Clear the dirs list in-place to stop os.walk from descending further
                    dirs[:] = []

                total_items += len(dirs) + len(files)

            self.preparation_finished.emit(total_items)

            if total_items == 0:
                self.finished.emit([])
                return

            file_data = []
            processed_items = 0
            # Second pass to process items, also respecting the depth limit
            for root, dirs, files in os.walk(self.directory, onerror=lambda err: print(f"Access error: {err}")):
                if not self.is_running: break

                # --- DEPTH LIMIT LOGIC (APPLIED AGAIN) ---
                current_depth = root.count(os.sep) - start_depth
                if self.limit_depth_enabled and current_depth >= self.max_depth:
                    dirs[:] = []

                all_items_in_root = [(name, True) for name in dirs] + [(name, False) for name in files]
                for name, is_dir in all_items_in_root:
                    if not self.is_running: break

                    path = os.path.join(root, name)
                    try:
                        metadata = self.get_file_metadata(path, self.metadata_cols, is_dir)
                        file_data.append(metadata)
                    except FileNotFoundError:
                        print(f"Skipping missing path or broken link: {path}")
                    except Exception as e:
                        print(f"Error processing '{path}': {e}")

                    processed_items += 1
                    self.progress_updated.emit(processed_items)

            if self.is_running:
                self.finished.emit(file_data)

        except Exception as e:
            import traceback
            error_message = f"A fatal error occurred in the worker thread: {e}\n\nTraceback:\n{traceback.format_exc()}"
            self.error.emit(error_message)

    def get_file_metadata(self, path, selected_metadata, is_dir=False):
        stat = os.stat(path)
        metadata = {}

        if "File Name" in selected_metadata: metadata["File Name"] = os.path.basename(path)
        if "Path" in selected_metadata: metadata["Path"] = path
        if "Size" in selected_metadata: metadata["Size"] = stat.st_size if not is_dir else ''
        if "Creation Time" in selected_metadata: metadata["Creation Time"] = datetime.fromtimestamp(
            stat.st_ctime).isoformat()
        if "Modification Time" in selected_metadata: metadata["Modification Time"] = datetime.fromtimestamp(
            stat.st_mtime).isoformat()
        if "Access Time" in selected_metadata: metadata["Access Time"] = datetime.fromtimestamp(
            stat.st_atime).isoformat()
        if "Type" in selected_metadata: metadata["Type"] = "Directory" if is_dir else (
            os.path.splitext(path)[1].upper() + " File" if os.path.splitext(path)[1] else "File")

        if "Owner" in selected_metadata:
            if IS_WINDOWS:
                metadata["Owner"] = "N/A (Windows)"
            else:
                try:
                    metadata["Owner"] = pwd.getpwuid(stat.st_uid).pw_name
                except (KeyError, AttributeError):
                    metadata["Owner"] = "N/A"

        if "Permissions" in selected_metadata: metadata["Permissions"] = oct(stat.st_mode & 0o777)
        return metadata

    def stop(self):
        self.is_running = False