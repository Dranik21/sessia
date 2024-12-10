
import sys
import hashlib
import uuid
import time
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget,
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QFileDialog, QCompleter
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PIL import Image


class CreateDriverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание водителя")

        # Поля ввода
        self.guid_field = QLineEdit(str(uuid.uuid4()))  # Генерация GUID
        self.guid_field.setReadOnly(True)
        self.last_name_field = QLineEdit()
        self.first_name_field = QLineEdit()
        self.middle_name_field = QLineEdit()
        self.passport_field = QLineEdit()
        self.passport_field.setPlaceholderText("Серия и номер (XXXX XXXXXX)")
        self.registration_address_field = QLineEdit()
        self.living_address_field = QLineEdit()
        self.workplace_field = QLineEdit()
        self.position_field = QLineEdit()
        self.phone_field = QLineEdit()
        self.phone_field.setPlaceholderText("+7XXXXXXXXXX")
        self.email_field = QLineEdit()
        self.photo_path_label = QLabel("Фото не выбрано")
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(100, 133)
        self.photo_preview.setStyleSheet("border: 1px solid black;")
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.notes_field = QLineEdit()
        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)
        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.validate_data)

        # Компоновка
        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор (GUID):", self.guid_field)
        form_layout.addRow("Фамилия*:", self.last_name_field)
        form_layout.addRow("Имя*:", self.first_name_field)
        form_layout.addRow("Отчество*:", self.middle_name_field)
        form_layout.addRow("Паспорт (серия и номер)*:", self.passport_field)
        form_layout.addRow("Адрес регистрации*:", self.registration_address_field)
        form_layout.addRow("Адрес проживания*:", self.living_address_field)
        form_layout.addRow("Место работы:", self.workplace_field)
        form_layout.addRow("Должность:", self.position_field)
        form_layout.addRow("Мобильный телефон*:", self.phone_field)
        form_layout.addRow("Email*:", self.email_field)
        photo_layout = QVBoxLayout()
        photo_layout.addWidget(self.photo_preview)
        photo_layout.addWidget(self.photo_path_label)
        photo_layout.addWidget(self.choose_photo_button)
        form_layout.addRow("Фотография*:", photo_layout)
        form_layout.addRow("Замечания:", self.notes_field)
        form_layout.addRow("", self.submit_button)
        self.setLayout(form_layout)

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фотографию", "", "Images (*.jpg *.png)")
        if file_path:
            try:
                image = Image.open(file_path)
                width, height = image.size
                file_size = os.path.getsize(file_path)
                if width / height != 3 / 4:
                    raise ValueError("Соотношение сторон изображения должно быть 3:4.")
                if height < width:
                    raise ValueError("Изображение должно быть вертикальным.")
                if file_size > 2 * 1024 * 1024:
                    raise ValueError("Размер изображения не должен превышать 2 МБ.")
                self.photo_path_label.setText(f"Фото выбрано: {os.path.basename(file_path)}")
                self.photo_preview.setPixmap(QPixmap(file_path).scaled(100, 133, Qt.KeepAspectRatio))
                self.photo_path = file_path
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def validate_data(self):
        errors = []
        if not self.last_name_field.text():
            errors.append("Фамилия обязательна.")
        if not self.first_name_field.text():
            errors.append("Имя обязательно.")
        if not self.middle_name_field.text():
            errors.append("Отчество обязательно.")
        if not self.passport_field.text() or not re.match(r"^\d{4}\s\d{6}$", self.passport_field.text()):
            errors.append("Паспорт должен быть в формате 'XXXX XXXXXX'.")
        if not self.registration_address_field.text():
            errors.append("Адрес регистрации обязателен.")
        if not self.living_address_field.text():
            errors.append("Адрес проживания обязателен.")
        if not self.phone_field.text() or not re.match(r"^\+7\d{10}$", self.phone_field.text()):
            errors.append("Телефон должен быть в формате '+7XXXXXXXXXX'.")
        if not self.email_field.text() or not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email_field.text()):
            errors.append("Email имеет неверный формат.")
        if not hasattr(self, 'photo_path') or not self.photo_path:
            errors.append("Фотография обязательна.")
        if errors:
            QMessageBox.warning(self, "Ошибки", "\n".join(errors))
        else:
            QMessageBox.information(self, "Успех", "Водитель успешно сохранен!")


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")
        self.setGeometry(810, 440, 300, 200)
        self.init_ui()

    def init_ui(self):
        create_driver_button = QPushButton("Создать водителя")
        create_driver_button.clicked.connect(self.open_create_driver_window)
        layout = QVBoxLayout()
        layout.addWidget(create_driver_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_create_driver_window(self):
        self.create_driver_window = CreateDriverWindow()
        self.create_driver_window.show()


class AuthSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.attempts = 0
        self.locked = False
        self.lock_time = 60  # блокировка на 60 секунд
        self.last_activity_time = time.time()
        self.setWindowTitle("Авторизация")
        self.setGeometry(810, 440, 300, 200)
        self.initUI()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel("Введите логин:")
        layout.addWidget(self.label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)
        self.label_password = QLabel("Введите пароль:")
        layout.addWidget(self.label_password)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_credentials)
        layout.addWidget(self.login_button)
        self.setCentralWidget(widget)
        widget.setLayout(layout)

        # Таймер блокировки
        self.lock_timer = QTimer()
        self.lock_timer.timeout.connect(self.unlock)

        # Таймер неактивности
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setInterval(60000)  # 1 минута
        self.inactivity_timer.timeout.connect(self.user_inactive)
        self.inactivity_timer.start()

    def check_credentials(self):
        if self.locked:
            QMessageBox.warning(self, "Ошибка", "У вас слишком много неудачных попыток входа. Попробуйте через 1 минуту.")
            return

        def hash(text):
            return hashlib.sha256(text.encode()).hexdigest()

        hash_password = '98fe442255035a1459bb5b86fda03d7c34c23d512b1b5bf3a5ecb7a802601895'

        username = self.username_input.text()
        password = self.password_input.text()
        hash_input_password = hash(password)

        # Проверка логина и пароля
        if username == "inspector" and hash_input_password == hash_password:
            QMessageBox.information(self, "Успех", "Добро пожаловать, inspector!")
            self.reset_attempts()
            self.open_main_window()
        else:
            self.attempts += 1
            self.last_activity_time = time.time()
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
            if self.attempts >= 3:
                self.locked = True
                self.login_button.setEnabled(False)
                self.lock_timer.start(60000)  # блокировка на 60 секунд
                QMessageBox.warning(self, "Блокировка", "Вход временно заблокирован. Попробуйте через 1 минуту.")

    def reset_attempts(self):
        self.attempts = 0
        self.locked = False
        self.login_button.setEnabled(True)

    def unlock(self):
        self.locked = False
        self.login_button.setEnabled(True)
        self.lock_timer.stop()
        self.attempts = 0

    def user_inactive(self):
        QMessageBox.warning(self, "Неактивность", "Вы были неактивны 1 минуту. Приложение закроется.")
        self.close()

    def open_main_window(self):
        self.main_window = MainApplication()
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthSystem()
    window.show()
    sys.exit(app.exec_())
