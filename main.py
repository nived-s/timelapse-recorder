import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog, messagebox
from rec_screen import ScreenRecorder
from speedup import TimeLapseConverter
import os
import time
import json
from screeninfo import get_monitors
import mss
from PIL import ImageTk, Image

CONFIG_FILE = "config.json"


class TimeLapseRecorder:
    def __init__(self):
        # Initialize display related variables
        self.available_displays = []
        self.current_display = None
        self.screen_capture = mss.mss()
        
        self.root = tk.Tk()
        self.root.title("Time Lapse Recorder")
        self.root.geometry("800x600")
        self.root.attributes('-alpha', 0.9)        # Initialize recorder
        self.recorder = None

        # Load saved path from config or use default
        self.output_path = self.load_config().get('last_path', os.path.join(os.getcwd(), 'recordings'))

        # Initialize timelapse converter
        self.converter = TimeLapseConverter(speed_factor=10)
        self.current_recording_path = None        # Set window icon
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
        self.display_combobox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
          # Bind display selection change
        self.display_combobox.bind('<<ComboboxSelected>>', self.on_display_change)
        
        # Initialize displays after creating combobox
        self.initialize_displays()
        
        # Create path selection label and entry
        self.path_label = ttk.Label(self.controls_frame, text="Output Path:")
        self.path_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))

        # Create a frame for path entry and browse button
        self.path_frame = ttk.Frame(self.controls_frame)
        self.path_frame.grid(
            row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.path_frame.columnconfigure(0, weight=1)

        self.path_var = tk.StringVar(value=self.output_path)
        self.path_entry = ttk.Entry(
            self.path_frame,
            textvariable=self.path_var,
            state='readonly'  # Make the entry read-only
        )
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.browse_button = ttk.Button(
            self.path_frame,
            text="Browse...",
            command=self.browse_directory
        )
        self.browse_button.grid(row=0, column=1, sticky=tk.E)

        # Create Start button with initial green style
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
        self.start_button.grid(row=0, column=1, rowspan=3,
                               sticky=(tk.E, tk.N), padx=(10, 0))

        # Configure controls frame grid
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.columnconfigure(1, weight=0)    
    
    def initialize_displays(self):
        """Initialize and store information about all available displays"""
        try:
            # Get all monitors using screeninfo
            monitors = get_monitors()
            
            # Store display information
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
            
            # Set default display to primary if available, otherwise first display
            self.current_display = next(
                (d for d in self.available_displays if d['is_primary']),
                self.available_displays[0] if self.available_displays else None
            )
            
            # Update combobox values if UI is initialized
            if hasattr(self, 'display_combobox'):
                self.update_display_list()
                
        except Exception as e:
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
            
    def update_display_list(self):
        """Update the display combobox with current display information"""
        if self.available_displays:
            display_names = [
                f"{d['name']} ({d['width']}x{d['height']})" + 
                (" (Primary)" if d['is_primary'] else "")
                for d in self.available_displays
            ]
            self.display_combobox['values'] = display_names
            
            # Select the current display in the combobox
            if self.current_display:
                current_index = next(
                    (i for i, d in enumerate(self.available_displays) 
                     if d['id'] == self.current_display['id']), 
                    0
                )
                self.display_combobox.current(current_index)

    def toggle_recording(self):
        if self.start_button['text'] == "Start":
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        # Get the current output path from the entry
        output_dir = self.path_var.get()

        # Validate the output directory
        if not os.path.exists(output_dir):
            tk.messagebox.showerror(
                "Error",
                "Output directory does not exist. Please select a valid directory."
            )
            return

        if not os.access(output_dir, os.W_OK):
            tk.messagebox.showerror(
                "Error",
                "Output directory is not writable. Please select another location."
            )
            return

        # Get current time and format it as HHMMSS_DDMMYY
        current_time = time.strftime("%H%M%S_%d%m%y")

        # Create temporary file for raw recording
        temp_file = os.path.join(output_dir, f'temp_{current_time}.mp4')
        self.current_recording_path = temp_file

        # Initialize recorder with temporary file
        self.recorder = ScreenRecorder(output_file=temp_file, fps=10)

        # Start recording
        self.recorder.start()

        # Update button text and colors
        self.start_button['text'] = "Stop"
        self.start_button['bg'] = '#f44336'  # Material Design Red
        self.start_button['activebackground'] = '#d32f2f'

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()

            # Convert to timelapse if we have a recording
            if self.current_recording_path and os.path.exists(self.current_recording_path):
                try:
                    # Create final timelapse file name
                    final_file = self.current_recording_path.replace(
                        'temp_', 'timelapse_')

                    # Convert to timelapse
                    self.converter.convert(
                        self.current_recording_path, final_file)

                    # Delete temporary file
                    os.remove(self.current_recording_path)
                except Exception as e:
                    print(f"Error creating timelapse: {e}")

            self.recorder = None
            self.current_recording_path = None

        # Update button text and colors
        self.start_button['text'] = "Start"
        self.start_button['bg'] = '#4CAF50'  # Material Design Green
        self.start_button['activebackground'] = '#45a049'

    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.path_var.get(),
            title="Select Output Directory"
        )
        if directory:  # If a directory was selected (not cancelled)
            try:
                # Try to create the directory if it doesn't exist
                os.makedirs(directory, exist_ok=True)
                # Test if the directory is writable
                test_file = os.path.join(directory, '.test_write')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    self.path_var.set(directory)
                    # Save the new path to config
                    self.save_config()
                except (IOError, OSError):
                    tk.messagebox.showerror(
                        "Error",
                        "Selected directory is not writable. Please choose another location."
                    )
            except (IOError, OSError):
                tk.messagebox.showerror(
                    "Error",
                    "Unable to create or access the selected directory. Please choose another location."
                )

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}

    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'last_path': self.path_var.get()
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")    
            
    def on_display_change(self, event):
        """Handle display selection changes"""
        selected_index = self.display_combobox.current()
        if selected_index >= 0 and selected_index < len(self.available_displays):
            self.current_display = self.available_displays[selected_index]

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TimeLapseRecorder()
    app.run()
