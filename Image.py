import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self):
        self.original_image = None   
        self.processed_image = None  

    def load_image(self, file_path):
        self.original_image = cv2.imread(file_path)
        return self.original_image is not None

    def process(self, alpha, enable_inversion):

        if self.original_image is None:
            return None

        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

        contrast_gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)

        if enable_inversion:
            self.processed_image = cv2.bitwise_not(contrast_gray)
        else:
            self.processed_image = contrast_gray

        return self.processed_image

    def save_image(self, save_path):
        if self.processed_image is not None:
            return cv2.imwrite(save_path, self.processed_image)
        return False

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Вариант 18: Линейный контраст + Инверсия")
        self.root.geometry("750x600")
        self.root.minsize(600, 500)

        self.processor = ImageProcessor()

        self.alpha_var = tk.DoubleVar(value=1.0)
        self.invert_var = tk.BooleanVar(value=False)

        self.orig_tk_image = None
        self.proc_tk_image = None

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_controls = ttk.Frame(self.notebook)
        self.tab_results = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_controls, text=" Управление и Исходник ")
        self.notebook.add(self.tab_results, text=" Результат обработки ")

        self.build_controls_tab()
        self.build_results_tab()

    def build_controls_tab(self):

        ctrl_frame = ttk.LabelFrame(self.tab_controls, text=" Параметры обработки ")
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_load = ttk.Button(ctrl_frame, text="Открыть изображение", command=self.open_file)
        btn_load.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        lbl_scale = ttk.Label(ctrl_frame, text="Контраст (Alpha):")
        lbl_scale.grid(row=0, column=1, padx=5, pady=10, sticky="e")
        
        scale_alpha = tk.Scale(
            ctrl_frame, from_=1.0, to=3.0, resolution=0.1, 
            variable=self.alpha_var, orient=tk.HORIZONTAL, length=150
        )
        scale_alpha.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        chk_invert = ttk.Checkbutton(
            ctrl_frame, text="Включить инверсию", variable=self.invert_var
        )
        chk_invert.grid(row=0, column=3, padx=15, pady=10, sticky="w")

        btn_process = ttk.Button(ctrl_frame, text="Обработать", command=self.process_image)
        btn_process.grid(row=0, column=4, padx=10, pady=10, sticky="e")

        preview_frame = ttk.LabelFrame(self.tab_controls, text=" Исходное изображение ")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.lbl_orig_img = ttk.Label(preview_frame, text="Изображение не загружено", anchor="center")
        self.lbl_orig_img.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_results_tab(self):

        save_frame = ttk.Frame(self.tab_results)
        save_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_save = ttk.Button(save_frame, text="Сохранить результат на диск", command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        res_frame = ttk.LabelFrame(self.tab_results, text=" Обработанный полутоновый кадр ")
        res_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.lbl_proc_img = ttk.Label(res_frame, text="Сначала выполните обработку на первой вкладке", anchor="center")
        self.lbl_proc_img.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def resize_for_preview(self, cv_img, max_w=600, max_h=400):

        h, w = cv_img.shape[:2]
        ratio = min(max_w / w, max_h / h)
        if ratio < 1.0:
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            return cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return cv_img

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            if self.processor.load_image(file_path):
                rgb_img = cv2.cvtColor(self.processor.original_image, cv2.COLOR_BGR2RGB)
                resized = self.resize_for_preview(rgb_img)
                
                pil_img = Image.fromarray(resized)
                self.orig_tk_image = ImageTk.PhotoImage(image=pil_img)
                self.lbl_orig_img.config(image=self.orig_tk_image, text="")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить выбранный файл!")

    def process_image(self):
        if self.processor.original_image is None:
            messagebox.showwarning("Внимание", "Пожалуйста, сначала откройте файл изображения!")
            return

        alpha = self.alpha_var.get()
        invert = self.invert_var.get()

        proc_matrix = self.processor.process(alpha=alpha, enable_inversion=invert)

        if proc_matrix is not None:
            resized = self.resize_for_preview(proc_matrix)
            
            pil_img = Image.fromarray(resized)
            self.proc_tk_image = ImageTk.PhotoImage(image=pil_img)
            
            self.lbl_proc_img.config(image=self.proc_tk_image, text="")
            
            self.notebook.select(self.tab_results)

    def save_file(self):
        if self.processor.processed_image is None:
            messagebox.showwarning("Внимание", "Нет обработанного изображения для сохранения!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG файл", "*.png"), ("JPEG файл", "*.jpg"), ("Все файлы", "*.*")]
        )
        
        if save_path:
            if self.processor.save_image(save_path):
                messagebox.showinfo("Успех", f"Файл успешно сохранен:\n{os.path.basename(save_path)}")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить файл.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()