import tkinter as tk
from PIL import ImageTk, Image


class PreviewCanvas:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg='#000', width=780, height=450)
        self.current_preview = None

    def show_image(self, pil_image):
        # Calculate scaling to fit canvas while maintaining aspect ratio
        canvas_width = int(self.canvas['width'])
        canvas_height = int(self.canvas['height'])
        img_width, img_height = pil_image.size
        scale_width = canvas_width / img_width if img_width > 0 else 1
        scale_height = canvas_height / img_height if img_height > 0 else 1
        scale = min(scale_width, scale_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        img = pil_image.resize((new_width, new_height),
                               Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.current_preview = photo
        self.canvas.create_image(x, y, image=photo, anchor="nw")
