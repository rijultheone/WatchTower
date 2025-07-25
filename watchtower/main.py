"""Main entry point for the Webcam Monitor application."""

import tkinter as tk
import sys
from pathlib import Path

from .gui.main_window import MainWindow

def main():
    """Main entry point."""
    try:
        # Create root window
        root = tk.Tk()
        
        # Set window icon if available
        icon_path = Path(__file__).parent / "resources" / "icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
            
        # Create main application window
        app = MainWindow(root)
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        import traceback
        error_msg = f"An unexpected error occurred:\n\n{str(e)}\n\n"
        error_msg += "".join(traceback.format_tb(e.__traceback__))
        
        # If GUI is available, show error dialog
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", error_msg)
        except:
            # Fallback to console
            print(error_msg, file=sys.stderr)
            
        sys.exit(1)

if __name__ == "__main__":
    main() 