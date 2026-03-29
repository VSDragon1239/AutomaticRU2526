import os
import sys

from PySide6.QtWidgets import QApplication, QDialog

from WorkSecureMoonBrowser.App.MoonBrowserEngine import MoonBrowser
from WorkSecureMoonBrowser.App.secure_launcher import LoginDialog


# def main():
#     app = QApplication(sys.argv)
#
#     # 1. Сначала показываем окно входа
#     # Пытаемся загрузить систему с пустым паролем, чтобы проверить наличие файла,
#     # но реальная инициализация внутри диалога
#     login_dlg = LoginDialog(None)
#
#     if login_dlg.exec() == QDialog.Accepted:
#         # 2. Если вход успешен, запускаем браузер
#         print(f"Доступ разрешен для: {login_dlg.user_authenticated}")
#
#         # Передаем путь к данным, как в прошлой версии
#         import os
#         data_path = "Moon_Data_Vault"
#         if not os.path.exists(data_path):
#             os.makedirs(data_path)
#
#         window = MoonBrowser(data_path)
#         window.show()
#         sys.exit(app.exec())
#     else:
#         sys.exit(0)
def main():
    app = QApplication(sys.argv)

    # # Показываем диалог входа
    # login = LoginDialog()
    #
    # if login.exec() == QDialog.Accepted:
    #     # Если вход успешен, запускаем браузер
    #     data_path = "Moon_Data_Vault"
    #     if not os.path.exists(data_path):
    #         os.makedirs(data_path)
    #
    #     window = MoonBrowser(data_path)
    #     window.show()
    #     sys.exit(app.exec())
    # else:
    #     sys.exit(0)
    data_path = "Moon_Data_Vault"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    window = MoonBrowser(data_path)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
