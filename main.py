import tkinter as tk
from tkinter import ttk, PhotoImage
from rec_screen import ScreenRecorder
import os
import time
import time


class TimeLapseRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Lapse Recorder")
        self.root.geometry("800x600")
        self.root.attributes('-alpha', 0.9)        # Initialize recorder
        self.recorder = None

        # Set window icon
        icon = PhotoImage(file="resources/cursor.png")
        self.root.iconphoto(False, icon)
        # Prevent window resizing (width, height)
        self.root.resizable(False, False)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        # Create display area (using Canvas for now, will be replaced with actual display later)
        self.display_area = tk.Canvas(
            self.main_frame, bg='#000', width=780, height=450)
        self.display_area.grid(row=0, column=0, columnspan=2, sticky=(
            tk.W, tk.E, tk.N, tk.S), pady=(20, 30), padx=20)

        # Add a separator for visual separation
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2,
                       sticky=(tk.W, tk.E), pady=(0, 20), padx=20)

        # Create controls frame
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.grid(row=2, column=0, columnspan=2, sticky=(
            tk.W, tk.E), padx=20, pady=(0, 20))

        # Create display selection dropdown
        self.display_var = tk.StringVar()
        self.display_combobox = ttk.Combobox(
            self.controls_frame,
            textvariable=self.display_var,
            state="readonly",
            width=50
        )
        # Will be populated with actual displays later
        self.display_combobox['values'] = ['Display 1']
        self.display_combobox.set('Display 1')
        self.display_combobox.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))        # Create Start button with initial green style
        self.start_button = tk.Button(
            self.controls_frame,
            text="Start",
            width=15,
            bg='#4CAF50',  # Material Design Green
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.RAISED,
            command=self.toggle_recording
        )
        self.start_button.grid(row=0, column=1, sticky=(tk.E), padx=(10, 0))

        # Configure controls frame grid
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.columnconfigure(1, weight=0)

    def toggle_recording(self):
        if self.start_button['text'] == "Start":
            self.start_recording()
        else:
            self.stop_recording()    
    
    def start_recording(self):
        # Create output directory if it doesn't exist
        os.makedirs('recordings', exist_ok=True)        # Get current time and format it as HHMMSS_DDMMYY
        current_time = time.strftime("%H%M%S_%d%m%y")
        output_file = os.path.join(
            'recordings', f'recording_{current_time}.mp4')
        self.recorder = ScreenRecorder(output_file=output_file, fps=10)

        # Start recording
        self.recorder.start()        # Update button text and colors
        self.start_button['text'] = "Stop"
        self.start_button['bg'] = '#f44336'  # Material Design Red
        self.start_button['activebackground'] = '#d32f2f'

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None

        # Update button text and colors
        self.start_button['text'] = "Start"
        self.start_button['bg'] = '#4CAF50'  # Material Design Green
        self.start_button['activebackground'] = '#45a049'

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TimeLapseRecorder()
    app.run()
