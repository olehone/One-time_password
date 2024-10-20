import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from controller import OTPController
from variables import title, geometry, seconds
from datetime import datetime


class OTPView(tk.Tk):
    def __init__(self, controller: OTPController):
        super().__init__()
        self.controller = controller
        self.title(title)
        self.geometry(geometry)
        self.label_var = tk.StringVar(value="test")
        key = self.controller.generate_secret_key()
        self.secret_var = tk.StringVar(value=key)
        self.otp_type_var = tk.StringVar(value="totp")
        self.counter_var = tk.StringVar(value="not used")
        self.qr_label = None
        self.interval = seconds
        self.create_widgets()
        self.updating()

    def run(self):
        self.mainloop()

    def create_widgets(self):
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="OTP Label:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        tk.Entry(form_frame, textvariable=self.label_var).grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Secret Key:").grid(
            row=1, column=0, sticky="w", padx=5
        )
        tk.Entry(form_frame, textvariable=self.secret_var, width=40).grid(
            row=1, column=1, columnspan=2, padx=5, sticky="we"
        )
        tk.Label(form_frame, text="OTP Type:").grid(row=2, column=0, sticky="w", padx=5)
        tk.Radiobutton(
            form_frame,
            text="time-based",
            variable=self.otp_type_var,
            value="totp",
            command=self.update_counter_visibility,
        ).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(
            form_frame,
            text="count-based",
            variable=self.otp_type_var,
            value="hotp",
            command=self.update_counter_visibility,
        ).grid(row=2, column=2, sticky="w")

        tk.Label(form_frame, text="Counter (for HOTP):").grid(
            row=3, column=0, sticky="w", padx=5
        )
        tk.Entry(form_frame, textvariable=self.counter_var).grid(
            row=3, column=1, padx=5
        )

        tk.Button(
            form_frame, text="Generate Secret Key", command=self.generate_secret_key
        ).grid(row=4, column=0, pady=10)
        tk.Button(form_frame, text="Add OTP", command=self.add_otp).grid(
            row=4, column=1, pady=10
        )
        self.otp_frame = tk.Frame(self)
        self.otp_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.timer_label = tk.Label(self, text="", font=("Helvetica", 12))
        self.timer_label.pack()

        self.qr_code_frame = tk.Frame(self)
        self.qr_code_frame.pack(pady=10)

    def update_counter_visibility(self):
        if self.otp_type_var.get() == "hotp":
            self.counter_var.set(value="0")
        else:
            self.counter_var.set(value="not used")

    def update_otp_list(self):
        for widget in self.otp_frame.winfo_children():
            widget.destroy()
        time_remaining = int(self.interval - datetime.now().timestamp() % self.interval)
        otps = self.controller.get_otps()
        for label, model in otps.items():
            type = model.type
            frame = tk.Frame(self.otp_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            code = self.controller.generate_otp(model)
            if type == "totp":
                result = f"Code: {code}  Time: {time_remaining}s"
            else:
                count = model.counter
                result = f"Code: {code}  Counter: {count}"
            label_text = tk.Label(frame, text=f"{label} - Code: {result}")
            label_text.pack(side=tk.LEFT)

            qr_button = tk.Button(
                frame,
                text="Generate QR",
                command=lambda l=label: self.show_qr_code(l),
            )
            qr_button.pack(side=tk.RIGHT)
            delete_button = tk.Button(
                frame,
                text="Delete",
                command=lambda l=label: self.delete_otp(l),
            )
            delete_button.pack(side=tk.RIGHT)
            if type == "hotp":
                count_button = tk.Button(
                    frame, text="Generate", command=lambda l=label: self.count_hotp(l)
                )
                count_button.pack(side=tk.RIGHT)

    def clean_fields(self):
        self.label_var.set("")
        self.secret_var.set("")
        self.otp_type_var.set(value="totp")
        self.counter_var.set(value="0")

    def generate_secret_key(self):
        key = self.controller.generate_secret_key()
        self.secret_var.set(key)
        return self.secret_var.get()

    def add_otp(self):
        label = self.label_var.get().strip()
        secret = self.secret_var.get().strip()
        otp_type = self.otp_type_var.get().strip()
        counter = int(self.counter_var.get()) if otp_type == "hotp" else None

        if otp_type == "hotp" and not self.controller.is_key_valid(secret):
            messagebox.showwarning(
                "Invalid Secret Key",
                "The secret key must be a valid Base32 encoded string.",
            )
            return

        if not label or not secret:
            messagebox.showwarning(
                "Input Error", "Please fill in both the label and secret key."
            )
            return

        self.controller.add_otp(label, secret, otp_type, counter)
        self.clean_fields()
        self.update_otp_list()
        self.show_qr_code(label)

    def delete_otp(self, label):
        self.controller.delete_otp(label)
        self.update_otp_list()

    def show_qr_code(self, label):
        model = self.controller.get_otp(label)
        if model:
            uri = self.controller.get_provisioning_uri(model, label)
            qr_img = self.controller.generate_qr_code(uri, label)
            img = qr_img.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            if self.qr_label:
                self.qr_label.config(image=img)
            else:
                self.qr_label = tk.Label(self.qr_code_frame, image=img)
                self.qr_label.pack()

            self.qr_label.image = img

    def count_hotp(self, label):
        otp = self.controller.generate_otp(self.controller.otp_manager.otps[label])
        self.controller.update_hotp_counter(label)
        self.show_qr_code(label)
        self.update_otp_list()

    def updating(self):
        self.update_otp_list()
        self.after(1000, self.updating)
