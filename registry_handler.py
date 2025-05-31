# registry_handler.py
import winreg
import sys
import os

# Using a more unique key name to avoid conflicts
CONTEXT_MENU_KEY_NAME = "PrintDirectoryPyTool"
BASE_KEY_PATH = r"Software\Classes\Directory\shell"
FULL_KEY_PATH = rf"{BASE_KEY_PATH}\{CONTEXT_MENU_KEY_NAME}"
COMMAND_SUBKEY_PATH = rf"{FULL_KEY_PATH}\command"

def get_pythonw_path():
    """Attempts to find the path to pythonw.exe."""
    python_exe_path = sys.executable
    # Construct path for pythonw.exe based on python.exe's location
    pythonw_exe_path = os.path.join(os.path.dirname(python_exe_path), "pythonw.exe")
    if os.path.exists(pythonw_exe_path):
        return pythonw_exe_path
    # Fallback if pythonw.exe is not next to python.exe (less common for standard installs)
    # This might need adjustment based on specific Python installation types (e.g., from MS Store)
    print(f"Warning: pythonw.exe not found at {pythonw_exe_path}. Trying sys.executable (might show console).")
    return python_exe_path # Fallback to python.exe, which will show a console

def check_context_menu_key_exists():
    """Checks if the application's context menu registry key exists."""
    try:
        # Try to open the key for reading
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, FULL_KEY_PATH, 0, winreg.KEY_READ):
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking registry key: {e}")
        return False

def add_context_menu_key(main_script_path):
    """Adds the context menu item to the Windows Registry."""
    pythonw_path = get_pythonw_path()
    if not main_script_path or not os.path.exists(main_script_path):
        return False, f"Invalid main script path: {main_script_path}"

    # Command to execute: "C:\path\to\pythonw.exe" "C:\path\to\main.py" "%1"
    # %1 is the placeholder for the selected directory path
    command_str = f'"{pythonw_path}" "{main_script_path}" "%1"'
    display_name = "Print Directory Contents (Py)" # Name shown in context menu

    try:
        # Create the main key: Software\Classes\Directory\shell\PrintDirectoryPyTool
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, FULL_KEY_PATH) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, display_name)
            # You can set an icon here if desired, e.g., from imageres.dll or your own .ico
            # winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "imageres.dll,7")

        # Create the command subkey: Software\Classes\Directory\shell\PrintDirectoryPyTool\command
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, COMMAND_SUBKEY_PATH) as cmd_key:
            winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, command_str)
        return True, "Context menu item added successfully."
    except PermissionError:
        return False, "Permission denied. Please run as administrator to modify the registry."
    except Exception as e:
        return False, f"Failed to add context menu item: {e}"

def remove_context_menu_key():
    """Removes the context menu item from the Windows Registry."""
    try:
        # It's important to delete subkeys before their parent keys.
        # Delete the command subkey first.
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, COMMAND_SUBKEY_PATH)
        # Then delete the main application key.
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, FULL_KEY_PATH)
        return True, "Context menu item removed successfully."
    except FileNotFoundError:
        # Key or subkey doesn't exist, which is fine if we're trying to remove it.
        return True, "Context menu item not found (or already removed)."
    except PermissionError:
        return False, "Permission denied. Please run as administrator to modify the registry."
    except Exception as e:
        return False, f"Failed to remove context menu item: {e}"