import tkinter as tk # для интерфейса
from tkinter import filedialog, messagebox, simpledialog
import cv2 # OpenCV для обработки
import numpy as np # для копий изображения(массивы)
from PIL import Image, ImageTk # для Tkinter


class ImageApp:
    """Приложение для обработки изображения."""

    def __init__(self, root):
        """Приложение с главным окном"""
        self.root = root
        self.root.title("Приложение для обработки изображений")
        self.image = None  # Исходное изображение в формате OpenCV (массив numpy)
        self.display_image = None  # Изображение для отображения в Tkinter
        self.modified = False  # Флаг для отслеживания изменений изображения

        # Создание элементов интерфейса
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_load = tk.Button(
            btn_frame, text="Загрузить изображение", command=self.load_image
        )
        self.btn_load.grid(row=0, column=0, padx=5)

        self.btn_camera = tk.Button(
            btn_frame, text="Сделать снимок с камеры", command=self.photo_camera
        )
        self.btn_camera.grid(row=0, column=1, padx=5)

        self.btn_exit = tk.Button(btn_frame, text="Выход", command=self.exit_app)
        self.btn_exit.grid(row=0, column=2, padx=5)

        self.canvas = tk.Canvas(root, width=600, height=400, bg="gray")
        self.canvas.pack()

        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        # Выбор цветового канала
        tk.Label(control_frame, text="Канал цвета:").grid(row=0, column=0)
        self.color_var = tk.StringVar(value="rgb")  # По умолчанию отображаем RGB
        tk.Radiobutton(
            control_frame,
            text="RGB",
            variable=self.color_var,
            value="rgb",
            command=self.show_image,
        ).grid(row=0, column=1)
        tk.Radiobutton(
            control_frame,
            text="Красный",
            variable=self.color_var,
            value="red",
            command=self.show_image,
        ).grid(row=0, column=2)
        tk.Radiobutton(
            control_frame,
            text="Зеленый",
            variable=self.color_var,
            value="green",
            command=self.show_image,
        ).grid(row=0, column=3)
        tk.Radiobutton(
            control_frame,
            text="Синий",
            variable=self.color_var,
            value="blue",
            command=self.show_image,
        ).grid(row=0, column=4)

        # Кнопки для обработки изображения
        self.btn_resize = tk.Button(
            control_frame, text="Изменить размер", command=self.resize_image
        )
        self.btn_resize.grid(row=1, column=0, pady=5)

        self.btn_brightness = tk.Button(
            control_frame, text="Понизить яркость", command=self.reduce_brightness
        )
        self.btn_brightness.grid(row=1, column=1)

        self.btn_draw_circle = tk.Button(
            control_frame, text="Нарисовать круг", command=self.draw_circle
        )
        self.btn_draw_circle.grid(row=1, column=2)

    def load_image(self):
        """Загрузка изображения из файла."""
        # Для типов изображения
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg")]
        )
        if file_path:
            try:
                img_cv = cv2.imread(file_path)
                if img_cv is None:
                    raise ValueError("Не удалось открыть изображение.")
                self.image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
                self.modified = False
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {e}")

    def photo_camera(self):
        """Захват изображения с веб-камеры."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror(
                "Ошибка",
                "Не удалось подключиться к веб-камере.\n"
                "Проверьте подключение или разрешения.",
            )
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            try:
                self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.modified = False
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке снимка: {e}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сделать снимок.")

    def show_image(self):
        """Отображение текущего изображения на канвасе с выбранным цветовым каналом."""
        if self.image is None:
            return

        img_copy = np.copy(self.image)

        # Применение выбранного цветового канала
        if self.color_var.get() == "rgb":
            img_single_channel = img_copy
        else:
            channel_idx = {"red": 0, "green": 1, "blue": 2}[self.color_var.get()]
            channels = [np.zeros_like(img_copy[:, :, i]) for i in range(3)]
            channels[channel_idx] = img_copy[:, :, channel_idx]
            img_single_channel = np.stack(channels, axis=-1)

        # Конвертация в PIL Image для отображения
        pil_img = Image.fromarray(img_single_channel)
        pil_img.thumbnail((600, 400))
        self.display_image_tk = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.display_image_tk)

    def resize_image(self):
        """Изменение размера текущего изображения."""
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            width_str = simpledialog.askstring("Введите ширину", "Ширина (пиксели):")
            height_str = simpledialog.askstring("Введите высоту", "Высота (пиксели):")
            if not width_str or not height_str:
                raise ValueError("Ширина и высота не могут быть пустыми.")
            width = int(width_str)
            height = int(height_str)
            if width <= 0 or height <= 0:
                raise ValueError("Ширина и высота должны быть положительными числами.")
            resized_img = cv2.resize(self.image, (width, height))
            self.image = resized_img
            self.modified = True
            self.show_image()
        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {ve}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при изменении размера: {e}")

    def reduce_brightness(self):
        """Уменьшение яркости текущего изображения."""
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            value_str = simpledialog.askstring(
                "Понизить яркость", "Введите значение уменьшения яркости (например 50):"
            )
            value = int(value_str)
            img_brightened = np.clip(self.image - value, 0, 255).astype(np.uint8)
            self.image = img_brightened
            self.modified = True
            self.show_image()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    def draw_circle(self):
        """Функция для красного круга."""
        if self.image is None:
            messagebox.showinfo("Информация", "Загрузите или сделайте снимок сначала.")
            return
        try:
            # Получение размеров изображения
            height, width = self.image.shape[:2]
            default_x = width // 2
            default_y = height // 2
            default_radius = min(width, height) // 10

            x_str = simpledialog.askstring(
                "Координата X",
                f"Введите координату X центра круга (по умолчанию {default_x}):",
            )
            y_str = simpledialog.askstring(
                "Координата Y",
                f"Введите координату Y центра круга (по умолчанию {default_y}):",
            )
            radius_str = simpledialog.askstring(
                "Радиус", f"Введите радиус круга (по умолчанию {default_radius}):"
            )

            # Использование центра изображения по умолчанию, если ввод пустой
            x_center = int(x_str) if x_str and x_str.strip() else default_x
            y_center = int(y_str) if y_str and x_str.strip() else default_y
            radius = int(radius_str) if radius_str and radius_str.strip() else default_radius

            # Проверка координат и радиуса
            if x_center < 0 or x_center >= width or y_center < 0 or y_center >= height:
                raise ValueError("Координаты центра круга выходят за пределы изображения.")
            if radius <= 0 or radius > min(width // 2, height // 2):
                raise ValueError(
                    "Радиус должен быть положительным и "
                    "не превышать половины размера изображения."
                )

            # Создание копии изображения
            img_copy = self.image.copy()

            # Рисование заполненного красного круга
            cv2.circle(img_copy, (x_center, y_center), radius, (255, 0, 0), -1)

            # Обновление изображения
            self.image = img_copy
            self.modified = True
            self.show_image()

        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректные параметры: {ve}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def exit_app(self):
        """Закрытие приложения."""
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()