import sys
import random
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QLabel,
                               QPushButton, QWidget, QGridLayout, QMessageBox, QHBoxLayout)
from PySide6.QtGui import QFont

# Импорт вашей системы аутентификации
from WorkSecureMoonBrowser.App.SecureAuth import SecureAuthSystem


class VirtualKeyboard(QWidget):
    def __init__(self, target_input=None):
        super().__init__()
        self.target_input = target_input
        self.setFixedSize(450, 180)

        main_layout = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setSpacing(2)

        # Перемешиваем клавиши для защиты от кейлоггеров
        keys = list("1234567890qwertyuiopasdfghjklzxcvbnm")
        random.shuffle(keys)

        for i, char in enumerate(keys):
            btn = QPushButton(char.upper())
            btn.setFixedSize(38, 38)
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton { background-color: #35363a; color: white; border-radius: 4px; }
                QPushButton:hover { background-color: #8e44ad; }
                QPushButton:pressed { background-color: #5f6368; }
            """)
            btn.clicked.connect(lambda checked, c=char: self.type_char(c))
            row = i // 10
            col = i % 10
            grid.addWidget(btn, row, col)

        main_layout.addLayout(grid)

        # Спец кнопки
        h_box = QHBoxLayout()
        btn_space = QPushButton("SPACE")
        btn_space.setStyleSheet("background: #2c3e50; color: white;")
        btn_space.clicked.connect(lambda: self.type_char(' '))

        btn_del = QPushButton("⌫")
        btn_del.setStyleSheet("background: #c0392b; color: white;")
        btn_del.clicked.connect(self.backspace)

        h_box.addWidget(btn_space)
        h_box.addWidget(btn_del)
        main_layout.addLayout(h_box)

    def set_target(self, input_field):
        self.target_input = input_field

    def type_char(self, char):
        if self.target_input:
            self.target_input.insert(char)

    def backspace(self):
        if self.target_input:
            self.target_input.backspace()


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔒 Доступ к Luna Browser")
        self.setFixedSize(550, 700)  # Увеличил размер под клавиатуру
        self.auth_system = None

        layout = QVBoxLayout(self)

        # Поля ввода
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Логин")
        layout.addWidget(QLabel("Имя пользователя:"))
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Мастер-пароль (используется для расшифровки и входа)")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.pass_input)

        self.totp_input = QLineEdit()
        self.totp_input.setPlaceholderText("123456")
        self.totp_input.setMaxLength(6)
        layout.addWidget(QLabel("Код 2FA:"))
        layout.addWidget(self.totp_input)

        # Кнопки входа
        btn_enter = QPushButton("Войти")
        btn_enter.setStyleSheet("background: #8e44ad; color: white; padding: 10px; font-weight: bold;")
        btn_enter.clicked.connect(self.try_login)
        layout.addWidget(btn_enter)

        # Переключатель клавиатуры
        self.kb_toggle = QPushButton("⌨️ Показать виртуальную клавиатуру")
        self.kb_toggle.setCheckable(True)
        self.kb_toggle.clicked.connect(self.toggle_kb)
        layout.addWidget(self.kb_toggle)

        # Сама клавиатура
        self.keyboard = VirtualKeyboard()
        self.keyboard.hide()
        layout.addWidget(self.keyboard)
        layout.addStretch()

        # Привязка фокуса к клавиатуре
        self.user_input.focusInEvent = lambda e: self.keyboard.set_target(self.user_input)
        self.pass_input.focusInEvent = lambda e: self.keyboard.set_target(self.pass_input)
        self.totp_input.focusInEvent = lambda e: self.keyboard.set_target(self.totp_input)

    def toggle_kb(self, checked):
        self.keyboard.show() if checked else self.keyboard.hide()

    def try_login(self):
        user = self.user_input.text()
        pwd = self.pass_input.text()
        otp = self.totp_input.text()

        if not user or not pwd:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            
            # 1. Инициализируем систему с мастер-паролем (он же пароль пользователя)
            self.auth_system = SecureAuthSystem(master_password=pwd)

            # 2. Пытаемся войти
            # Передаем 'pwd' как пароль, так как в нашей схеме Мастер-пароль = Пароль пользователя
            result = self.auth_system.authenticate(
                username=user,
                password=pwd,
                two_factor_code=otp
            )

            if result['success']:
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка доступа", result['message'])

        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка",
                                 f"Не удалось расшифровать базу данных.\nВероятно, неверный Мастер-пароль.\n\n{e}")