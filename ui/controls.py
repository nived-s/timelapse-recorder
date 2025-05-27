import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
from PIL import Image, ImageTk
import win32gui


class ControlsFrame:
    def __init__(self, parent, config_manager, display_manager, recorder, timelapse_converter, preview):
        self.frame = ttk.Frame(parent)
        self.config_manager = config_manager
        self.display_manager = display_manager
        self.recorder = recorder
        self.timelapse_converter = timelapse_converter
        self.preview = preview
        self.available_displays = self.display_manager.get_available_displays()
        self.current_display = self.display_manager.get_current_display()
        self.output_path = self.config_manager.load_config().get(
            'last_path', os.path.join(os.getcwd(), 'recordings'))
        self.current_recording_path = None
        self.preview_running = True

        # Load the custom cursor image for preview
        self.cursor_img = Image.open('resources/cursor.png').resize((24, 24))

        # Display selection dropdown
        self.display_var = tk.StringVar()
        self.display_combobox = ttk.Combobox(
            self.frame,
            textvariable=self.display_var,
            state="readonly",
            width=50
        )
        self.display_combobox['values'] = [f"{d['name']} ({d['width']}x{d['height']})" + (
            " (Primary)" if d['is_primary'] else "") for d in self.available_displays]
        self.display_combobox.set(
            self.display_combobox['values'][0] if self.display_combobox['values'] else '')
        self.display_combobox.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.display_combobox.bind(
            '<<ComboboxSelected>>', self.on_display_change)

        # Path selection
        self.path_label = ttk.Label(self.frame, text="Output Path:")
        self.path_label.grid(row=1, column=0, sticky=tk.W,
                             padx=(0, 10), pady=(10, 0))
        self.path_frame = ttk.Frame(self.frame)
        self.path_frame.grid(
            row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.path_frame.columnconfigure(0, weight=1)
        self.path_var = tk.StringVar(value=self.output_path)
        self.path_entry = ttk.Entry(
            self.path_frame, textvariable=self.path_var, state='readonly')
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.browse_button = ttk.Button(
            self.path_frame, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=0, column=1, sticky=tk.E)

        # Start/Stop button
        self.start_button = tk.Button(
            self.frame,
            text="Start",
            width=15,
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.RAISED,
            command=self.toggle_recording
        )
        self.start_button.grid(row=0, column=1, rowspan=3,
                               sticky=(tk.E, tk.N), padx=(10, 0))
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=0)
        self.start_preview_loop()
        self.capture_and_show_preview()

    def on_display_change(self, event):
        selected_index = self.display_combobox.current()
        if selected_index >= 0 and selected_index < len(self.available_displays):
            selected_display = self.available_displays[selected_index]
            self.current_display = selected_display
            self.display_manager.set_current_display(selected_display['id'])
            self.capture_and_show_preview()
            self.save_config()

    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.path_var.get(),
            title="Select Output Directory"
        )
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                test_file = os.path.join(directory, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                self.path_var.set(directory)
                self.save_config()
            except Exception:
                messagebox.showerror(
                    "Error", "Unable to create or access the selected directory. Please choose another location.")

    def toggle_recording(self):
        if self.start_button['text'] == "Start":
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        output_dir = self.path_var.get()
        if not os.path.exists(output_dir):
            messagebox.showerror(
                "Error", "Output directory does not exist. Please select a valid directory.")
            return
        if not os.access(output_dir, os.W_OK):
            messagebox.showerror(
                "Error", "Output directory is not writable. Please select another location.")
            return
        current_time = time.strftime("%H%M%S_%d%m%y")
        temp_file = os.path.join(output_dir, f'temp_{current_time}.mp4')
        self.recorder.output_file = temp_file
        self.recorder.fps = 10
        self.recorder.capture_region = {
            'left': self.current_display['x'],
            'top': self.current_display['y'],
            'width': self.current_display['width'],
            'height': self.current_display['height']
        }
        self.current_recording_path = temp_file
        self.recorder.start()
        self.start_button['text'] = "Stop"
        self.start_button['bg'] = '#f44336'
        self.start_button['activebackground'] = '#d32f2f'

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            if self.current_recording_path and os.path.exists(self.current_recording_path):
                try:
                    final_file = self.current_recording_path.replace(
                        'temp_', 'timelapse_')
                    self.timelapse_converter.convert(
                        self.current_recording_path, final_file)
                    os.remove(self.current_recording_path)
                except Exception as e:
                    print(f"Error creating timelapse: {e}")
            self.recorder = None
            self.current_recording_path = None
        self.start_button['text'] = "Start"
        self.start_button['bg'] = '#4CAF50'
        self.start_button['activebackground'] = '#45a049'

    def save_config(self):
        config = {
            'last_path': self.path_var.get(),
            'display': {
                'id': self.current_display['id'],
                'name': self.current_display['name'],
                'width': self.current_display['width'],
                'height': self.current_display['height'],
                'x': self.current_display['x'],
                'y': self.current_display['y']
            } if self.current_display else None
        }
        self.config_manager.save_config(config)

    def capture_and_show_preview(self):
        try:
            import mss
            screen_capture = mss.mss()
            screenshot = screen_capture.grab(self.current_display['geometry'])
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            # Draw cursor on preview
            img = self.draw_cursor_on_preview(img)
            self.preview.show_image(img)
        except Exception as e:
            print(f"Error updating preview: {e}")

    def draw_cursor_on_preview(self, img):
        try:
            cursor_pos = win32gui.GetCursorPos()
            cursor_x = cursor_pos[0] - self.current_display['x']
            cursor_y = cursor_pos[1] - self.current_display['y']
            if (0 <= cursor_x < self.current_display['width'] and
                0 <= cursor_y < self.current_display['height']):
                result = img.copy()
                result.paste(self.cursor_img, (int(cursor_x), int(cursor_y)), self.cursor_img)
                return result
            return img
        except Exception as e:
            print(f"Error drawing cursor on preview: {e}")
            return img

    def start_preview_loop(self):
        # Always start the preview loop
        self.update_preview()

    def stop_preview_loop(self):
        self.preview_running = False

    def update_preview(self):
        if self.preview_running:
            if not getattr(self.recorder, 'is_recording', False):
                self.capture_and_show_preview()
            self.frame.after(33, self.update_preview)
