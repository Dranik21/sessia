import sys
import hashlib
import time
import uuid
import re
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget,
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QFileDialog, QCompleter
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
from PIL import Image


class CreateDriverWindow(QWidget):
    def init(self):
        super().init()
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
        self.registration_city_field = QLineEdit()
        self.registration_address_field = QLineEdit()
        self.living_city_field = QLineEdit()
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

        # Автодополнение для городов
        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
        completer = QCompleter(cities)
        self.registration_city_field.setCompleter(completer)
        self.living_city_field.setCompleter(completer)

        # Компоновка
        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор (GUID):", self.guid_field)
        form_layout.addRow("Фамилия*:", self.last_name_field)
        form_layout.addRow("Имя*:", self.first_name_field)
        form_layout.addRow("Отчество*:", self.middle_name_field)
        form_layout.addRow("Паспорт*:", self.passport_field)
        form_layout.addRow("Город регистрации*:", self.registration_city_field)
        form_layout.addRow("Адрес регистрации*:", self.registration_address_field)
        form_layout.addRow("Город проживания*:", self.living_city_field)
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
        if not self.registration_city_field.text():
            errors.append("Город регистрации обязателен.")
        if not self.registration_address_field.text():
            errors.append("Адрес регистрации обязателен.")
        if not self.living_city_field.text():
            errors.append("Город проживания обязателен.")
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
    def init(self):
        super().init()
        self.setWindowTitle("Главное окно")
        self.setGeometry(800, 400, 400, 200)
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
    def init(self):
        super().init()
        self.setWindowTitle("Авторизация")
        self.setGeometry(800, 400, 300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_field)

        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Пароль")
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_field)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.check_credentials)
        layout.addWidget(login_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
def check_credentials(self):
        username = self.username_field.text()
        password = self.password_field.text()
        if username == "admin" and password == "12345":
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")

def open_main_window(self):
    self.main_window = MainApplication()
    self.main_window.show()
    self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_system = AuthSystem()
    auth_system.show()
    sys.exit(app.exec_())