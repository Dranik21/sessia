import sys
import hashlib
import uuid
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget,
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image

# Словарь для хранения данных водителей
drivers_db = {}

class DriverLicenseWindow(QWidget):
    def init(self):
        super().init()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Регистрация ВУ")

        # Поля ввода для ВУ
        self.driver_id_field = QLineEdit()  # Ввод идентификатора водителя
        self.driver_id_field.setPlaceholderText("Идентификатор водителя (GUID)")
        self.license_number_field = QLineEdit()  # Номер удостоверения
        self.license_number_field.setPlaceholderText("Номер удостоверения")
        self.issue_date_field = QLineEdit()  # Дата выдачи
        self.expiry_date_field = QLineEdit()  # Дата окончания действия
        self.issuing_authority_field = QLineEdit()  # Орган, выдавший удостоверение
        self.vehicle_categories_field = QLineEdit()  # Категории транспортных средств
        self.driver_photo_label = QLabel("Фото не выбрано")  # Фото водителя
        self.driver_photo_preview = QLabel()
        self.driver_photo_preview.setFixedSize(100, 133)
        self.driver_photo_preview.setStyleSheet("border: 1px solid black;")
        self.driver_photo_preview.setAlignment(Qt.AlignCenter)
        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)

        # Кнопка для сохранения данных
        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.save_driver_license)

        # Компоновка формы
        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор водителя (GUID):", self.driver_id_field)
        form_layout.addRow("Номер удостоверения:", self.license_number_field)
        form_layout.addRow("Дата выдачи:", self.issue_date_field)
        form_layout.addRow("Дата окончания действия:", self.expiry_date_field)
        form_layout.addRow("Орган, выдавший удостоверение:", self.issuing_authority_field)
        form_layout.addRow("Категории транспортных средств:", self.vehicle_categories_field)
        photo_layout = QVBoxLayout()
        photo_layout.addWidget(self.driver_photo_preview)
        photo_layout.addWidget(self.driver_photo_label)
        photo_layout.addWidget(self.choose_photo_button)
        form_layout.addRow("Фото водителя:", photo_layout)
        form_layout.addRow("", self.submit_button)
        self.setLayout(form_layout)

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фотографию", "", "Images (*.jpg *.png)")
        if file_path:
            try:
                image = Image.open(file_path)
                self.driver_photo_label.setText(f"Фото выбрано: {os.path.basename(file_path)}")
                self.driver_photo_preview.setPixmap(QPixmap(file_path).scaled(100, 133, Qt.KeepAspectRatio))
                self.photo_path = file_path
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def save_driver_license(self):
        driver_id = self.driver_id_field.text()
        license_number = self.license_number_field.text()
        issue_date = self.issue_date_field.text()
        expiry_date = self.expiry_date_field.text()
        issuing_authority = self.issuing_authority_field.text()
        vehicle_categories = self.vehicle_categories_field.text()

        if not driver_id or not license_number or not issue_date or not expiry_date or not issuing_authority or not vehicle_categories:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка существования водителя в базе
        if driver_id not in drivers_db:
            QMessageBox.warning(self, "Ошибка", "Водитель с таким ID не найден. Добавьте его в систему.")
            return
            # Добавляем данные ВУ для водителя
            drivers_db[driver_id]["licenses"].append({
                "license_number": license_number,
                "issue_date": issue_date,
                "expiry_date": expiry_date,
                "issuing_authority": issuing_authority,
                "vehicle_categories": vehicle_categories,
                "photo_path": getattr(self, 'photo_path', None)
            })

            QMessageBox.information(self, "Успех", "ВУ успешно зарегистрировано!")

class AddDriverWindow(QWidget):
    def init(self):
        super().init()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавление водителя")

        # Поля ввода
        self.driver_id_field = QLineEdit(str(uuid.uuid4()))  # Генерация нового GUID для водителя
        self.last_name_field = QLineEdit()
        self.first_name_field = QLineEdit()
        self.middle_name_field = QLineEdit()
        self.dob_field = QLineEdit()  # Дата рождения водителя
        self.photo_field = QLabel("Фото не выбрано")
        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)
        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.save_driver)

        # Компоновка
        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор водителя (GUID):", self.driver_id_field)
        form_layout.addRow("Фамилия:", self.last_name_field)
        form_layout.addRow("Имя:", self.first_name_field)
        form_layout.addRow("Отчество:", self.middle_name_field)
        form_layout.addRow("Дата рождения:", self.dob_field)
        form_layout.addRow("Фото водителя:", self.photo_field)
        form_layout.addRow("", self.submit_button)
        self.setLayout(form_layout)

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фотографию", "", "Images (*.jpg *.png)")
        if file_path:
            self.photo_field.setText(f"Фото выбрано: {os.path.basename(file_path)}")
            self.photo_path = file_path

    def save_driver(self):
        driver_id = self.driver_id_field.text()
        last_name = self.last_name_field.text()
        first_name = self.first_name_field.text()
        middle_name = self.middle_name_field.text()
        dob = self.dob_field.text()

        if not last_name or not first_name or not middle_name or not dob:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        # Добавляем водителя в базу данных
        drivers_db[driver_id] = {
            "last_name": last_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "dob": dob,
            "licenses": []  # Список ВУ для водителя
        }

        QMessageBox.information(self, "Успех", "Водитель успешно добавлен!")

class MainApplication(QMainWindow):
    def init(self):
        super().init()
        self.setWindowTitle("Главное окно")
        self.setGeometry(810, 440, 300, 200)
        self.init_ui()

    def init_ui(self):
        add_driver_button = QPushButton("Добавить водителя")
        add_driver_button.clicked.connect(self.open_add_driver_window)
        register_license_button = QPushButton("Зарегистрировать ВУ")
        register_license_button.clicked.connect(self.open_register_license_window)
        layout = QVBoxLayout()
        layout.addWidget(add_driver_button)
        layout.addWidget(register_license_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_add_driver_window(self):
        self.add_driver_window = AddDriverWindow()
        self.add_driver_window.show()

    def open_register_license_window(self):
        self.register_license_window = DriverLicenseWindow()
        self.register_license_window.show()

class AuthSystem(QMainWindow):
    def init(self):
        super().init()
        self.attempts = 0
        self.locked = False
        self.lock_time = 60  # блокировка на 60 секунд
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

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "inspector" and password == "12345":
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def open_main_window(self):
        self.main_window = MainApplication()
        self.main_window.show()
        self.close()  # Закрытие окна авторизации


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthSystem()
    window.show()
    sys.exit(app.exec_())