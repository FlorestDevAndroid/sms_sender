import subprocess
import time
import shlex

# write here your path, where adb.exe exists.
ADB_PATH = "adb"


def send_sms(phone_number, message):
    # Экранируем аргументы для Android shell
    phone = shlex.quote(f"smsto:{phone_number}")
    text = shlex.quote(message)

    subprocess.run([
        ADB_PATH,
        "shell",
        "am", "start",
        "-a", "android.intent.action.SENDTO",
        "-d", phone,
        "--es", "sms_body", text
    ], check=True)

    time.sleep(2)

    subprocess.run([
        ADB_PATH,
        "shell",
        "input", "tap",
        "1121", "2437"
    ], check=True)


send_sms(
    input("Введи номер телефона: "),
    input("Введи сообщение: ")
)
