import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import cv2
import numpy as np

class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Advanced Image Filtering App")
        self.root.geometry("1200x700")

        # Variabel gambar
        self.original_img = None
        self.filtered_img = None
        self.history = []

        # Frame utama
        self.main_frame = tk.Frame(root, bg="#f0f2f5")
        self.main_frame.pack(fill="both", expand=True)

        # Bagian kiri (gambar)
        self.image_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        self.image_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.label_original = tk.Label(self.image_frame, text="Original", font=("Arial", 12, "bold"), bg="#f0f2f5")
        self.label_original.pack()
        self.canvas_original = tk.Label(self.image_frame, bg="white")
        self.canvas_original.pack(pady=5)

        self.label_filtered = tk.Label(self.image_frame, text="Filtered", font=("Arial", 12, "bold"), bg="#f0f2f5")
        self.label_filtered.pack()
        self.canvas_filtered = tk.Label(self.image_frame, bg="white")
        self.canvas_filtered.pack(pady=5)

        # Bagian kanan (kontrol)
        self.control_frame = tk.Frame(self.main_frame, bg="#e9ecef")
        self.control_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Style tombol
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("TLabel", background="#e9ecef")

        # Tombol load/save/reset
        ttk.Label(self.control_frame, text="🖼 Image Controls", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(self.control_frame, text="Load Image", command=self.load_image).pack(fill="x", pady=2)
        ttk.Button(self.control_frame, text="Save Filtered", command=self.save_image).pack(fill="x", pady=2)
        ttk.Button(self.control_frame, text="Undo", command=self.undo).pack(fill="x", pady=2)
        ttk.Button(self.control_frame, text="Reset All", command=self.reset_all).pack(fill="x", pady=2)

        # Slider real-time
        ttk.Label(self.control_frame, text="⚡ Real-Time Adjustments", font=("Arial", 12, "bold")).pack(pady=10)

        self.add_slider("Brightness", 0.5, 3.0, 1.0, self.update_filter)
        self.add_slider("Contrast", 0.5, 3.0, 1.0, self.update_filter)
        self.add_slider("Blur", 0, 10, 0, self.update_filter)
        self.add_slider("Rotate", 0, 360, 0, self.update_filter)

        # Quick filters
        ttk.Label(self.control_frame, text="🎨 Quick Filters", font=("Arial", 12, "bold")).pack(pady=10)
        filters = [
            ("Grayscale", self.apply_grayscale),
            ("Invert", self.apply_invert),
            ("Sharpen", lambda: self.apply_filter(ImageFilter.SHARPEN)),
            ("Edge Enhance", lambda: self.apply_filter(ImageFilter.EDGE_ENHANCE)),
            ("Emboss", lambda: self.apply_filter(ImageFilter.EMBOSS)),
            ("Sepia", self.apply_sepia),
            ("Cartoonify", self.apply_cartoon),
            ("Pencil Sketch", self.apply_sketch),
            ("Flip Horizontal", lambda: self.apply_filter("FLIP_H")),
            ("Flip Vertical", lambda: self.apply_filter("FLIP_V"))
        ]
        for name, cmd in filters:
            ttk.Button(self.control_frame, text=name, command=cmd).pack(fill="x", pady=2)

    # Tambah slider dengan label angka
    def add_slider(self, name, frm, to, default, command):
        frame = tk.Frame(self.control_frame, bg="#e9ecef")
        frame.pack(fill="x", pady=3)

        label = ttk.Label(frame, text=name)
        label.pack(side="left")

        var = tk.DoubleVar(value=default)
        slider = ttk.Scale(frame, from_=frm, to=to, variable=var, orient="horizontal", command=lambda e: command())
        slider.pack(side="left", fill="x", expand=True, padx=5)

        value_label = ttk.Label(frame, text=f"{default:.2f}")
        value_label.pack(side="right")

        slider.var = var
        slider.value_label = value_label
        setattr(self, f"{name.lower()}_slider", slider)

    def load_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if file:
            self.original_img = Image.open(file).convert("RGB")
            self.filtered_img = self.original_img.copy()
            self.history = [self.original_img.copy()]
            self.display_images()

    def save_image(self):
        if self.filtered_img:
            file = filedialog.asksaveasfilename(defaultextension=".png")
            if file:
                self.filtered_img.save(file)

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.filtered_img = self.history[-1].copy()
            self.display_images()

    def reset_all(self):
        if self.original_img:
            self.filtered_img = self.original_img.copy()
            self.history = [self.original_img.copy()]
            for slider in [self.brightness_slider, self.contrast_slider, self.blur_slider, self.rotate_slider]:
                slider.var.set(1.0 if "ness" in slider._name or "trast" in slider._name else 0)
            self.display_images()

    def update_filter(self):
        if not self.original_img:
            return
        img = self.original_img.copy()

        # Ambil nilai slider
        brightness = self.brightness_slider.var.get()
        contrast = self.contrast_slider.var.get()
        blur = int(self.blur_slider.var.get())
        rotate = int(self.rotate_slider.var.get())

        # Update angka slider
        for slider in [self.brightness_slider, self.contrast_slider, self.blur_slider, self.rotate_slider]:
            slider.value_label.config(text=f"{slider.var.get():.2f}")

        # Apply filter
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        if blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(blur))
        if rotate != 0:
            img = img.rotate(rotate)

        self.filtered_img = img
        self.history.append(img.copy())
        self.display_images()

    def apply_filter(self, filter_type):
        if not self.filtered_img:
            return
        img = self.filtered_img.copy()
        if filter_type == "FLIP_H":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif filter_type == "FLIP_V":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            img = img.filter(filter_type)
        self.filtered_img = img
        self.history.append(img.copy())
        self.display_images()

    def apply_grayscale(self):
        if self.filtered_img:
            self.filtered_img = ImageOps.grayscale(self.filtered_img).convert("RGB")
            self.history.append(self.filtered_img.copy())
            self.display_images()

    def apply_invert(self):
        if self.filtered_img:
            img = self.filtered_img.convert("RGB")
            self.filtered_img = ImageOps.invert(img)
            self.history.append(self.filtered_img.copy())
            self.display_images()

    def apply_sepia(self):
        if not self.filtered_img:
            return
        img = np.array(self.filtered_img.convert("RGB"))
        tr = 0.393 * img[:, :, 0] + 0.769 * img[:, :, 1] + 0.189 * img[:, :, 2]
        tg = 0.349 * img[:, :, 0] + 0.686 * img[:, :, 1] + 0.168 * img[:, :, 2]
        tb = 0.272 * img[:, :, 0] + 0.534 * img[:, :, 1] + 0.131 * img[:, :, 2]
        sepia = np.stack([tr, tg, tb], axis=2).clip(0, 255).astype(np.uint8)
        self.filtered_img = Image.fromarray(sepia)
        self.history.append(self.filtered_img.copy())
        self.display_images()

    def apply_cartoon(self):
        if not self.filtered_img:
            return
        img = np.array(self.filtered_img.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(edges, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        self.filtered_img = Image.fromarray(cartoon)
        self.history.append(self.filtered_img.copy())
        self.display_images()

    def apply_sketch(self):
        if not self.filtered_img:
            return
        img = np.array(self.filtered_img.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        self.filtered_img = Image.fromarray(sketch).convert("RGB")
        self.history.append(self.filtered_img.copy())
        self.display_images()

    def display_images(self):
        if not self.original_img or not self.filtered_img:
            return

        def resize_img(img, max_size=(400, 400)):
            img = img.copy()
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            return img

        orig_disp = ImageTk.PhotoImage(resize_img(self.original_img))
        filt_disp = ImageTk.PhotoImage(resize_img(self.filtered_img))

        self.canvas_original.config(image=orig_disp)
        self.canvas_original.image = orig_disp
        self.canvas_filtered.config(image=filt_disp)
        self.canvas_filtered.image = filt_disp


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()
