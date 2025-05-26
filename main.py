import tkinter as tk
from tkinter import ttk, PhotoImage

class TimeLapseRecorder:    
    def __init__(self):
        self.root = tk.Tk()        
        self.root.title("Time Lapse Recorder")
        self.root.geometry("800x600")
        
        # Set window icon
        icon = PhotoImage(file="resources/cursor.png")
        self.root.iconphoto(False, icon)
        self.root.resizable(False, False)  # Prevent window resizing (width, height)
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
        self.display_area = tk.Canvas(self.main_frame, bg='white', width=780, height=450)
        self.display_area.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 30), padx=20)
        
        # Add a separator for visual separation
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20), padx=20)
        
        # Create controls frame
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20, pady=(0, 20))
        
        # Create display selection dropdown
        self.display_var = tk.StringVar()
        self.display_combobox = ttk.Combobox(
            self.controls_frame, 
            textvariable=self.display_var,
            state="readonly",
            width=50
        )
        self.display_combobox['values'] = ['Display 1']  # Will be populated with actual displays later
        self.display_combobox.set('Display 1')        
        self.display_combobox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Create Start button
        self.start_button = ttk.Button(
            self.controls_frame,
            text="Start",
            width=15,
            style='Accent.TButton'  # Add custom style for emphasis
        )
        self.start_button.grid(row=0, column=1, sticky=(tk.E), padx=(10, 0))
        
        # Configure controls frame grid
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.columnconfigure(1, weight=0)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TimeLapseRecorder()
    app.run()