from screeninfo import get_monitors
import tkinter as tk


class DisplayManager:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.available_displays = []
        self.current_display = None
        self.detect_displays()

    def detect_displays(self):
        try:
            monitors = get_monitors()
            self.available_displays = []
            for i, monitor in enumerate(monitors):
                display_info = {
                    'id': i,
                    'name': f"Display {i+1}",
                    'width': monitor.width,
                    'height': monitor.height,
                    'x': monitor.x,
                    'y': monitor.y,
                    'is_primary': monitor.is_primary,
                    'geometry': {
                        'top': monitor.y,
                        'left': monitor.x,
                        'width': monitor.width,
                        'height': monitor.height
                    }
                }
                self.available_displays.append(display_info)
            # Set current display to primary or first
            self.current_display = next(
                (d for d in self.available_displays if d['is_primary']),
                self.available_displays[0] if self.available_displays else None
            )
        except Exception:
            # Fallback to single display mode
            self.available_displays = [{
                'id': 0,
                'name': "Display 1",
                'width': self.root.winfo_screenwidth(),
                'height': self.root.winfo_screenheight(),
                'x': 0,
                'y': 0,
                'is_primary': True,
                'geometry': {
                    'top': 0,
                    'left': 0,
                    'width': self.root.winfo_screenwidth(),
                    'height': self.root.winfo_screenheight()
                }
            }]
            self.current_display = self.available_displays[0]

    def get_available_displays(self):
        return self.available_displays

    def get_current_display(self):
        return self.current_display

    def set_current_display(self, display_id):
        for d in self.available_displays:
            if d['id'] == display_id:
                self.current_display = d
                return d
        return None
