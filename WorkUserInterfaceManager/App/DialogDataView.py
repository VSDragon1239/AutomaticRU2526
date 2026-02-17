from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton


class DialogDataView(QDialog):
    list_data = []

    def __init__(self, data_title_name, count_data, parent=None):
        super().__init__(parent)
        self.count_data = count_data
        self.setWindowTitle(f"Новый «{data_title_name}»")

        self.layout = QVBoxLayout(self)

        # Метка и поле ввода
        if data_title_name != "Приложение":
            if self.count_data == 1:
                self.resize(400, 100)
                self.layout.addWidget(QLabel(f"Введите название:"))
                self.NameEdit = QLineEdit(self)
                self.layout.addWidget(self.NameEdit)
            elif self.count_data == 2:
                self.resize(450, 200)
                self.layout.addWidget(QLabel(f"Введите название:"))
                self.NameEdit = QLineEdit(self)
                self.layout.addWidget(self.NameEdit)

                self.layout.addWidget(QLabel(f"Введите описание:"))
                self.DescriptionEdit = QLineEdit(self)
                self.layout.addWidget(self.DescriptionEdit)
            elif self.count_data == 3:
                self.resize(500, 300)
                self.layout.addWidget(QLabel(f"Введите название:"))
                self.NameEdit = QLineEdit(self)
                self.layout.addWidget(self.NameEdit)

                self.layout.addWidget(QLabel(f"Введите тип: ( Будет редактироваться... )"))
                self.TypeEdit = QLineEdit(self)
                self.layout.addWidget(self.TypeEdit)

                self.layout.addWidget(QLabel(f"Введите описание:"))
                self.DescriptionEdit = QLineEdit(self)
                self.layout.addWidget(self.DescriptionEdit)
            else:
                raise ValueError("Указанное количество не зарегистрировано! Используйте от 1 до 3! ")
        elif self.count_data == 5:
            # """app_name, app_type, app_desc, app_path, icon_path"""
            self.resize(500, 300)
            self.layout.addWidget(QLabel(f"Введите название:"))
            self.NameEdit = QLineEdit(self)
            self.layout.addWidget(self.NameEdit)

            self.layout.addWidget(QLabel(f"Введите тип (Не используется):"))
            self.TypeEdit = QLineEdit(self)
            self.layout.addWidget(self.TypeEdit)

            self.layout.addWidget(QLabel(f"Введите Описание..."))
            self.DescriptionEdit = QLineEdit(self)
            self.layout.addWidget(self.DescriptionEdit)

            self.layout.addWidget(QLabel(f"Введите путь к .exe файлу..."))
            self.ExePathEdit = QLineEdit(self)
            self.layout.addWidget(self.ExePathEdit)

            self.layout.addWidget(QLabel(f"Введите путь к .ico файлу..."))
            self.IcoPathEdit = QLineEdit(self)
            self.layout.addWidget(self.IcoPathEdit)

        # Кнопки OK / Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        # button1 = QPushButton("Проверка данных")
        # button1.clicked.connect(self.print_gn)
        # self.layout.addWidget(button1)

    def returr(self):
        self.list_data = []
        if self.count_data == 1:
            self.list_data.append(self.NameEdit.text().strip())
        elif self.count_data == 2:
            self.list_data.insert(0, self.NameEdit.text().strip())
            self.list_data.insert(1, self.DescriptionEdit.text().strip())
        elif self.count_data == 3:
            self.list_data.append(self.NameEdit.text().strip())
            self.list_data.append(self.TypeEdit.text().strip())
            self.list_data.append(self.DescriptionEdit.text().strip())
        elif self.count_data == 5:
            self.list_data.append(self.NameEdit.text().strip())
            self.list_data.append(self.TypeEdit.text().strip())
            self.list_data.append(self.DescriptionEdit.text().strip())
            self.list_data.append(self.ExePathEdit.text().strip())
            self.list_data.append(self.IcoPathEdit.text().strip())
        else:
            return None

    def get_name(self):
        if self.exec() == QDialog.Accepted:
            self.returr()
            return self.list_data
        return None
