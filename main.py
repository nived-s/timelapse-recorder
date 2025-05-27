import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog, messagebox

import os
import time

from ui.main_window import MainWindow
from config.config_manager import ConfigManager
from core.display_manager import DisplayManager
from core.recorder import ScreenRecorder
from core.timelapse import TimeLapseConverter


def main():
    root = tk.Tk()
    config_manager = ConfigManager()
    display_manager = DisplayManager(root)
    recorder = ScreenRecorder()
    timelapse_converter = TimeLapseConverter(speed_factor=10)
    app = MainWindow(config_manager, display_manager,
                     recorder, timelapse_converter, root)
    app.run()


if __name__ == "__main__":
    main()
