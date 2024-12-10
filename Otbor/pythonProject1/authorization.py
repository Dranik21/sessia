import sys
import hashlib
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QWidget,
                             QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PyQt5.QtCore import QTimer

class AuthSystem(QMainWindow):
    def __init__(self):
        super().__init__()

        self.attempts = 0
        self.locked = False
        self.lock_time = 60  # блокировка на 60 секунд
        self.last_activity_time = time.time()

        self.setWindowTitle("Авторизация")
        self.setGeometry(810, 440, 350, 20)

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
        hash_passworld = '98fe442255035a1459bb5b86fda03d7c34c23d512b1b5bf3a5ecb7a802601895'


        username = self.username_input.text()
        password = self.password_input.text()
        hash_in_passworld = hash(password)

        # Проверка логина и пароля
        if username == "inspector" and hash_in_passworld == hash_passworld:
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
                self.lock_timer.start(60000)  # запускаем таймер блокировки
                QMessageBox.warning(self, "Блокировка", "Вместо этого попробуйте через 1 минуту.")

    def reset_attempts(self):
        self.attempts = 0
        self.locked = False
        self.login_button.setEnabled(True)

    def unlock(self):
        """Снятие блокировки."""
        self.locked = False
        self.login_button.setEnabled(True)
        self.lock_timer.stop()
        self.attempts = 0

    def user_inactive(self):
        """Закрытие приложения при бездействии."""
        self.close()

    def keyPressEvent(self, event):
        """Сброс таймера неактивности при нажатии клавиш."""
        self.last_activity_time = time.time()
        self.inactivity_timer.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthSystem()
    window.show()
    sys.exit(app.exec_())