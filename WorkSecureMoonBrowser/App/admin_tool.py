import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QLabel, QLineEdit, QPushButton, QMessageBox,
                               QFormLayout, QGroupBox)
from PySide6.QtGui import QPixmap, QImage, Qt
from io import BytesIO
import qrcode

# Импортируем класс безопасности
# Обратите внимание на путь, он должен соответствовать вашей структуре
from WorkSecureMoonBrowser.App.SecureAuth import SecureAuthSystem


class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Moon Admin: Создание пользователя")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        group = QGroupBox("Данные нового пользователя")
        form = QFormLayout(group)

        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)

        form.addRow("Логин:", self.user_edit)
        form.addRow("Мастер-пароль:", self.pass_edit)

        btn_create = QPushButton("Создать и показать QR")
        btn_create.clicked.connect(self.create_user)

        layout.addWidget(group)
        layout.addWidget(btn_create)

        self.qr_label = QLabel("QR код появится здесь")
        self.qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)

    def create_user(self):
        u = self.user_edit.text()
        p = self.pass_edit.text()

        if not u or not p:
            QMessageBox.warning(self, "Внимание", "Заполните поля!")
            return

        try:
            # Используем тот же класс, что и в браузере
            auth = SecureAuthSystem(master_password=p)
            res = auth.register_user(username=u, password=p)

            if res['success']:
                # Генерируем картинку QR
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(res['uri'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qimg = QImage.fromData(buffer.getvalue())
                self.qr_label.setPixmap(QPixmap.fromImage(qimg))

                QMessageBox.information(self, "Успех", "Пользователь создан! Файл users.json обновлен.")
            else:
                QMessageBox.critical(self, "Ошибка", res.get('message', 'Unknown error'))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AdminPanel()
    w.show()
    sys.exit(app.exec())
