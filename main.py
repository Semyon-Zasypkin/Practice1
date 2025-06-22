import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import numpy as np


class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Базовое приложение для обработки изображений")
        self.image = None  # исходное изображение в формате OpenCV (numpy array)
        self.display_image = None  # изображение для отображения в интерфейсе

        # Создаем элементы интерфейса
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_load = tk.Button(btn_frame, text="Загрузить изображение", command=self.load_image)
        self.btn_load.grid(row=0, column=0, padx=5)

        self.btn_camera = tk.Button(btn_frame, text="Сделать снимок с камеры", command=self.capture_from_camera)
        self.btn_camera.grid(row=0, column=1, padx=5)

        self.canvas = tk.Canvas(root, width=600, height=400, bg='gray')
        self.canvas.pack()

        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        # Канал цвета
        tk.Label(control_frame, text="Канал цвета:").grid(row=0, column=0)
        self.color_var = tk.StringVar(value='red')
        tk.Radiobutton(control_frame, text='Красный', variable=self.color_var, value='red',
                       command=self.show_image).grid(row=0, column=1)
        tk.Radiobutton(control_frame, text='Зеленый', variable=self.color_var, value='green',
                       command=self.show_image).grid(row=0, column=2)
        tk.Radiobutton(control_frame, text='Синий', variable=self.color_var, value='blue',
                       command=self.show_image).grid(row=0, column=3)

        # Размер изображения
        self.btn_resize = tk.Button(control_frame, text="Изменить размер", command=self.resize_image)
        self.btn_resize.grid(row=1, column=0, pady=5)

        # Понижение яркости
        self.btn_brightness = tk.Button(control_frame, text="Понизить яркость", command=self.reduce_brightness)
        self.btn_brightness.grid(row=1, column=1)

        # Нарисовать круг
        self.btn_draw_circle = tk.Button(control_frame, text="Нарисовать круг", command=self.draw_circle)
        self.btn_draw_circle.grid(row=1, column=2)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            try:
                img_cv = cv2.imread(file_path)
                if img_cv is None:
                    raise ValueError("Не удалось открыть изображение.")
                self.image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)  # переводим в RGB для PIL
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {e}")

    def capture_from_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка",
                                 "Не удалось подключиться к веб-камере.\nПроверьте подключение или разрешения.")
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            try:
                self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке снимка: {e}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сделать снимок.")

    def show_image(self):
        if self.image is None:
            return

        # Вырезаем выбранный канал
        channel_idx = {'red': 0, 'green': 1, 'blue': 2}[self.color_var.get()]

        img_copy = np.copy(self.image)

        # Создаем изображение с одним каналом (остальные черные)
        channels = [np.zeros_like(img_copy[:, :, i]) for i in range(3)]

        channels[channel_idx] = img_copy[:, :, channel_idx]

        img_single_channel = np.stack(channels, axis=-1)

        # Конвертируем в PIL Image для отображения
        pil_img = Image.fromarray(img_single_channel)

        # Масштабируем изображение под размер канваса (если нужно)
        pil_img.thumbnail((600, 400))

        self.display_image_tk = ImageTk.PhotoImage(pil_img)

        # Обновляем канвас
        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.display_image_tk)

    def resize_image(self):
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            width_str = simpledialog.askstring("Введите ширину", "Ширина (пиксели):")
            height_str = simpledialog.askstring("Введите высоту", "Высота (пиксели):")
            width = int(width_str)
            height = int(height_str)
            resized_img = cv2.resize(self.image, (width, height))
            self.image = resized_img
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    def reduce_brightness(self):
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            value_str = simpledialog.askstring("Понизить яркость", "Введите значение уменьшения яркости (например 50):")
            value = int(value_str)
            # Уменьшаем яркость каждого канала
            img_brightened = np.clip(self.image - value, 0, 255).astype(np.uint8)
            self.image = img_brightened
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    def draw_circle(self):
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            x_str = simpledialog.askstring("Координата X", "Введите координату X центра круга:")
            y_str = simpledialog.askstring("Координата Y", "Введите координату Y центра круга:")
            radius_str = simpledialog.askstring("Радиус", "Введите радиус круга:")

            x_center = int(x_str)
            y_center = int(y_str)
            radius = int(radius_str)

            color_input = simpledialog.askstring("Цвет круга", "Введите цвет круга: красный/зеленый/синий").lower()

            color_map = {
                'красный': (255, 0, 0),
                'зеленый': (0, 255, 0),
                'синий': (0, 0, 255),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
            }

            circle_color = (255, 0, 0) if color_input == 'красный' or color_input == 'red' else \
                (0, 255, 0) if color_input == 'зеленый' or color_input == 'green' else \
                    (0, 0, 255) if color_input == 'синий' or color_input == 'blue' else \
                        (255, 255, 255)  # по умолчанию белый

            img_with_circle = np.copy(self.image)

            # Рисуем круг на изображении OpenCV (BGR формат!)

            cv2.circle(img_with_circle, (x_center, y_center), radius, circle_color, -1)  # залитый круг

            # Обновляем изображение и показываем его

            self.image = cv2.cvtColor(img_with_circle, CV2_BGR_TO_RGB)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректные параметры: {e}")
        finally:
            self.show_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()