import subprocess
import time
import shlex
import tkinter as tk
from tkinter import messagebox
from threading import Thread


ADB_PATH = "adb"

SEND_X = 1121
SEND_Y = 2437


class SMSApp:
    def __init__(self, root):
        self.root = root

        self.root.title("SMS Creator")
        self.root.geometry("500x620")
        self.root.resizable(False, False)

        self.bg = "#111318"
        self.panel = "#1a1d24"
        self.input_bg = "#242832"
        self.fg = "#ffffff"
        self.muted = "#9da3ae"
        self.accent = "#4f8cff"
        self.success = "#4caf50"
        self.error = "#ff5252"

        self.root.configure(bg=self.bg)

        self.build_ui()

        # Вместо блокирующего while True
        self.root.after(100, self.loop)

    def build_ui(self):
        # Заголовок
        title = tk.Label(
            self.root,
            text="SMS Creator",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg,
            fg=self.fg
        )
        title.pack(pady=(25, 5))

        subtitle = tk.Label(
            self.root,
            text="Отправка SMS через ADB",
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.muted
        )
        subtitle.pack(pady=(0, 20))

        # Основная панель
        panel = tk.Frame(
            self.root,
            bg=self.panel
        )
        panel.pack(
            padx=25,
            fill="both",
            expand=True
        )

        # Номер
        tk.Label(
            panel,
            text="Номер телефона",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.fg
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 7)
        )

        self.phone_entry = tk.Entry(
            panel,
            font=("Segoe UI", 12),
            bg=self.input_bg,
            fg=self.fg,
            insertbackground=self.fg,
            relief="flat"
        )
        self.phone_entry.pack(
            padx=25,
            fill="x",
            ipady=10
        )

        # Сообщение
        tk.Label(
            panel,
            text="Сообщение",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.fg
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 7)
        )

        self.message_text = tk.Text(
            panel,
            height=8,
            font=("Segoe UI", 11),
            bg=self.input_bg,
            fg=self.fg,
            insertbackground=self.fg,
            relief="flat",
            wrap="word"
        )
        self.message_text.pack(
            padx=25,
            fill="x"
        )

        # Кнопка
        self.send_button = tk.Button(
            panel,
            text="Отправить SMS",
            font=("Segoe UI", 11, "bold"),
            bg=self.accent,
            fg="white",
            activebackground="#3d73d8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.start_send
        )
        self.send_button.pack(
            padx=25,
            pady=25,
            fill="x",
            ipady=10
        )

        # Статус
        tk.Label(
            panel,
            text="Статус",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel,
            fg=self.fg
        ).pack(
            anchor="w",
            padx=25
        )

        self.status_label = tk.Label(
            panel,
            text="Готов к работе",
            font=("Segoe UI", 10),
            bg=self.panel,
            fg=self.muted,
            anchor="w"
        )
        self.status_label.pack(
            padx=25,
            pady=(5, 20),
            fill="x"
        )

    def log(self, text, color=None):
        if color is None:
            color = self.muted

        self.status_label.config(
            text=text,
            fg=color
        )

    def start_send(self):
        phone = self.phone_entry.get().strip()
        message = self.message_text.get("1.0", "end-1c")

        if not phone:
            messagebox.showwarning(
                "Ошибка",
                "Введите номер телефона."
            )
            return

        if not message:
            messagebox.showwarning(
                "Ошибка",
                "Введите сообщение."
            )
            return

        self.send_button.config(
            state="disabled",
            text="Отправка..."
        )

        self.log(
            f"Подготовка SMS на {phone}...",
            self.muted
        )

        # Не блокируем Tkinter
        Thread(
            target=self.send_sms,
            args=(phone, message),
            daemon=True
        ).start()

    def send_sms(self, phone_number, message):
        try:
            phone = shlex.quote(
                f"smsto:{phone_number}"
            )

            text = shlex.quote(message)

            # Открываем SMS
            subprocess.run([
                ADB_PATH,
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.SENDTO",
                "-d",
                phone,
                "--es",
                "sms_body",
                text
            ], check=True)

            time.sleep(2)

            # Нажимаем "Отправить"
            subprocess.run([
                ADB_PATH,
                "shell",
                "input",
                "tap",
                str(SEND_X),
                str(SEND_Y)
            ], check=True)

            self.root.after(
                0,
                lambda: self.send_finished(True)
            )

        except subprocess.CalledProcessError as e:
            self.root.after(
                0,
                lambda: self.send_finished(
                    False,
                    str(e)
                )
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: self.send_finished(
                    False,
                    str(e)
                )
            )

    def send_finished(self, success, error=None):
        self.send_button.config(
            state="normal",
            text="Отправить SMS"
        )

        if success:
            self.log(
                "✓ SMS успешно отправлено",
                self.success
            )
        else:
            self.log(
                f"✗ Ошибка: {error}",
                self.error
            )

    def loop(self):
        """
        Аналог while True, но безопасный для Tkinter.

        Tkinter сам управляет главным циклом,
        поэтому настоящий while True здесь использовать нельзя.
        """
        # Здесь можно выполнять периодические проверки.

        # Например:
        # проверять подключение ADB
        # проверять устройство
        # обновлять статус

        self.root.after(100, self.loop)


root = tk.Tk()

app = SMSApp(root)

root.mainloop()
