import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from functools import partial
from controller import OTPController
from variables import title, geometry, seconds, padding, qr_img_size
from datetime import datetime


class OTPView:

    def __init__(self, controller: OTPController):
        self.controller = controller
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry(geometry)
        self.otp_frames = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.label_var = ctk.StringVar(value="Назва")
        self.secret_var = ctk.StringVar(value=self.controller.generate_secret_key())
        self.otp_type_var = ctk.StringVar(value="totp")
        self.counter_var = ctk.StringVar(value="Не використовується")
        self.interval = seconds

        self.qr_label = None
        self.create_widgets()
        self.updating()

    def run(self):
        self.root.mainloop()

    def update_otp_list(self):
        time_remaining = int(self.interval - datetime.now().timestamp() % self.interval)
        otps = self.controller.get_otps()

        labels_to_delete = set(self.otp_frames.keys()) - set(otps.keys())

        for label in labels_to_delete:
            frame = self.otp_frames.pop(label)
            frame.destroy()
        for label, model in otps.items():
            otp_code = self.controller.generate_otp(model)
            result = self._format_otp_display(model, otp_code, time_remaining)

            if label in self.otp_frames:
                existing_frame = self.otp_frames[label]
                existing_label = existing_frame.winfo_children()[0]
                existing_label.configure(text=f"{label} - {result}")
            else:
                self._create_otp_display(label, model, time_remaining)

    def _create_otp_display(self, label, model, time_remaining):
        otp_code = self.controller.generate_otp(model)
        result = self._format_otp_display(model, otp_code, time_remaining)

        frame = ctk.CTkFrame(self.otp_frame)
        frame.pack(fill="x", padx=5, pady=5)

        label_widget = ctk.CTkLabel(frame, text=f"{label} - {result}")
        label_widget.pack(side="left")

        self.otp_frames[label] = frame
        self._create_otp_buttons(frame, label, model.type)

    def _create_otp_buttons(self, frame, label, otp_type):
        ctk.CTkButton(
            frame, text="QR-код", command=partial(self.show_qr_code, label)
        ).pack(side="right")

        ctk.CTkButton(
            frame, text="Видалити", command=partial(self.delete_otp, label)
        ).pack(side="right")

        if otp_type == "hotp":
            ctk.CTkButton(
                frame, text="Отримати", command=partial(self.count_hotp, label)
            ).pack(side="right")

    def _format_otp_display(self, model, otp_code, time_remaining):
        if model.type == "totp":
            return f"{otp_code}  Часу лишилось: {time_remaining}с"
        return f"{otp_code}  Лічильник: {model.counter}"

    def create_widgets(self):
        form_frame = ctk.CTkFrame(self.root)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self._create_label_entry(
            form_frame, "Назва одноразового паролю:", self.label_var, row=0
        )
        self._create_label_entry(form_frame, "Секретний ключ:", self.secret_var, row=1)

        ctk.CTkLabel(form_frame, text="Тип паролю:").grid(
            row=2, column=0, **padding, sticky="w"
        )
        self._create_radio_buttons(form_frame)

        self._create_label_entry(
            form_frame,
            "Лічильник(для залежного від лічильника):",
            self.counter_var,
            row=3,
        )

        ctk.CTkButton(
            form_frame,
            text="Згенерувати секретний ключ",
            command=self.generate_secret_key,
        ).grid(row=4, column=0, pady=10)
        ctk.CTkButton(form_frame, text="Додати до списку", command=self.add_otp).grid(
            row=4, column=1, pady=10
        )

        self.otp_frame = ctk.CTkFrame(self.root)
        self.otp_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.timer_label = ctk.CTkLabel(self.root, text="", font=("Helvetica", 12))
        self.timer_label.pack()

        self.qr_code_frame = ctk.CTkFrame(self.root)
        self.qr_code_frame.pack(pady=10)

    def _create_label_entry(self, parent, text, variable, row):
        ctk.CTkLabel(parent, text=text).grid(row=row, column=0, **padding, sticky="w")
        entry = ctk.CTkEntry(parent, textvariable=variable)
        entry.grid(row=row, column=1, **padding, columnspan=2)

    def _create_radio_buttons(self, parent):
        ctk.CTkRadioButton(
            parent,
            text="Залежний від часу",
            variable=self.otp_type_var,
            value="totp",
            command=self.update_counter_visibility,
        ).grid(row=2, column=1, **padding)
        ctk.CTkRadioButton(
            parent,
            text="Залежний від лічильника",
            variable=self.otp_type_var,
            value="hotp",
            command=self.update_counter_visibility,
        ).grid(row=2, column=2, **padding)

    def update_counter_visibility(self):
        self.counter_var.set(
            "0" if self.otp_type_var.get() == "hotp" else "Не використовується"
        )

    def generate_secret_key(self):
        self.secret_var.set(self.controller.generate_secret_key())

    def add_otp(self):
        label, secret, otp_type, counter = self._get_otp_form_values()

        if not self._validate_input(label, secret, otp_type):
            return

        self.controller.add_otp(label, secret, otp_type, counter)
        self.update_otp_list()
        self.show_qr_code(label)

    def _get_otp_form_values(self):
        label = self.label_var.get().strip()
        secret = self.secret_var.get().strip()
        otp_type = self.otp_type_var.get().strip()
        counter = int(self.counter_var.get()) if otp_type == "hotp" else None
        return label, secret, otp_type, counter

    def _validate_input(self, label, secret, otp_type):
        if otp_type == "hotp" and not self.controller.is_key_valid(secret):
            messagebox.showwarning(
                "Неправильний секретний ключ",
                "Секретний ключ має бути закодованим рядком Base32.",
            )
            return False
        if not label or not secret:
            messagebox.showwarning(
                "Помилка Введення", "Будь ласка, введіть назву та ключ"
            )
            return False
        return True

    def delete_otp(self, label):
        self.controller.delete_otp(label)
        self.update_otp_list()

    def show_qr_code(self, label):
        otp = self.controller.get_provisioning_uri(label)
        if otp:
            qr_image = self.controller.generate_qr_code(otp)
            img = ctk.CTkImage(light_image=qr_image, size=[qr_img_size, qr_img_size])
            if self.qr_label:
                self.qr_label.configure(image=img)
            else:
                self.qr_label = ctk.CTkLabel(self.qr_code_frame, image=img, text="")
                self.qr_label.pack(pady=10)
            self.qr_label.image = img

    def updating(self):
        self.update_otp_list()
        self.root.after(1000, self.updating)

    def count_hotp(self, label):
        self.controller.update_hotp_counter(label)
        self.update_otp_list()
