import tkinter as tk
from tkinter import ttk, PhotoImage
from ui.controls import ControlsFrame
from ui.preview import PreviewCanvas


class MainWindow:
    def __init__(self, config_manager, display_manager, recorder, timelapse_converter, root):
        self.root = root
        self.root.title("Time Lapse Recorder")
        self.root.geometry("800x600")
        self.root.attributes('-alpha', 0.9)
        self.root.resizable(False, False)
        # Set window icon with error handling and keep reference
        try:
            self.icon = PhotoImage(file="resources/cursor.png")
            self.root.iconphoto(False, self.icon)
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        # Preview area
        self.preview = PreviewCanvas(self.main_frame)
        self.preview.canvas.grid(row=0, column=0, columnspan=2, sticky=(
            tk.W, tk.E, tk.N, tk.S), pady=(20, 30), padx=20)

        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2,
                       sticky=(tk.W, tk.E), pady=(0, 20), padx=20)

        # Controls
        self.controls = ControlsFrame(
            self.main_frame, config_manager, display_manager, self.preview)
        self.controls.frame.grid(row=2, column=0, columnspan=2, sticky=(
            tk.W, tk.E), padx=20, pady=(0, 20))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)

        # Add speed factor slider below controls
        self.controls.add_speed_slider(
            initial_value=timelapse_converter.speed_factor,
            min_value=1,
            max_value=60,
            callback=self.on_speed_change,
            slider_length=180  # Set a reasonable width for the slider
        )

    def on_speed_change(self, event=None):
        # Placeholder for now, will connect to timelapse_converter in next step
        pass

    def run(self):
        self.root.mainloop()
