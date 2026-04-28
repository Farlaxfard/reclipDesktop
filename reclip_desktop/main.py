import os
import sys
import threading
import webview
from app import app

# Global window reference
main_window = None

class Api:
    def choose_directory(self):
        """Opens a native folder selection dialog."""
        window = webview.active_window() or (webview.windows[0] if webview.windows else None)
        if not window: return None
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if isinstance(result, (list, tuple)) and result else result

    def open_dev_tools(self):
        """Opens the developer tools for the active window."""
        window = webview.active_window()
        if window: window.open_devtools()

    def toggle_dev_mode_window(self, is_dark):
        """Opens a separate window for Developer Mode settings."""
        port = int(os.environ.get("PORT", 8899))
        dev_window = webview.create_window(
            "Developer Mode",
            f"http://127.0.0.1:{port}/dev_mode?dark={'true' if is_dark else 'false'}",
            width=400, height=500,
            resizable=False,
            easy_drag=True
        )
        dev_window.events.closed += self.on_dev_mode_close

    def on_dev_mode_close(self):
        """Callback when the developer mode window is closed."""
        if main_window:
            main_window.evaluate_js("if(typeof onDevModeClosed === 'function') onDevModeClosed();")

def run_flask():
    """Starts the Flask server on a local loopback."""
    port = int(os.environ.get("PORT", 8899))
    # Optimization: debug=False and use_reloader=False for faster startup
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Flask in a background thread for faster window launch
    threading.Thread(target=run_flask, daemon=True).start()

    # Launch the pywebview window
    port = int(os.environ.get("PORT", 8899))
    api = Api()
    
    # Optimization: Set window background to match theme for perceived speed
    main_window = webview.create_window(
        "ReClip", 
        f"http://127.0.0.1:{port}", 
        width=1024, height=768, 
        easy_drag=True, 
        js_api=api,
        background_color='#f4f1eb' # Matches light mode
    )
    
    webview.start()
