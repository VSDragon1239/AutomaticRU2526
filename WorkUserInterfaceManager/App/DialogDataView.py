from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QFileDialog, \
    QHBoxLayout


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
            self.resize(550, 350)

            self._add_field("Введите название:", "NameEdit")
            self._add_field("Введите тип (Не используется):", "TypeEdit")
            self._add_field("Введите Описание...", "DescriptionEdit")

            # Поле EXE с кнопкой
            self.layout.addWidget(QLabel("Введите путь к .exe файлу:"))
            exe_layout = QHBoxLayout()
            self.ExePathEdit = QLineEdit(self)
            self.ExePathEdit.setPlaceholderText("Например: C:/Projects/App.exe")
            exe_layout.addWidget(self.ExePathEdit)

            self.ExeBrowseBtn = QPushButton("📁 Обзор...")
            self.ExeBrowseBtn.setFixedWidth(100)
            self.ExeBrowseBtn.clicked.connect(self._browse_exe)
            exe_layout.addWidget(self.ExeBrowseBtn)
            self.layout.addLayout(exe_layout)

            # Поле ICO с кнопкой
            self.layout.addWidget(QLabel("Введите путь к .ico файлу:"))
            ico_layout = QHBoxLayout()
            self.IcoPathEdit = QLineEdit(self)
            self.IcoPathEdit.setPlaceholderText("Необязательно: C:/Icons/App.ico")
            ico_layout.addWidget(self.IcoPathEdit)

            self.IcoBrowseBtn = QPushButton("📁 Обзор...")
            self.IcoBrowseBtn.setFixedWidth(100)
            self.IcoBrowseBtn.clicked.connect(self._browse_ico)
            ico_layout.addWidget(self.IcoBrowseBtn)
            self.layout.addLayout(ico_layout)

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

    def _add_field(self, label_text, attr_name):
        """Вспомогательный метод для создания полей ввода"""
        self.layout.addWidget(QLabel(label_text))
        edit = QLineEdit(self)
        setattr(self, attr_name, edit)
        self.layout.addWidget(edit)

    def _browse_exe(self):
        """Открывает диалог выбора .exe файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите исполняемый файл",
            "",
            "Исполняемые файлы (*.exe);;Ярлыки (*.lnk);;Все файлы (*.*)"
        )
        if file_path:
            self.ExePathEdit.setText(file_path.replace("\\", "/"))

    def _browse_ico(self):
        """Открывает диалог выбора .ico файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл иконки",
            "",
            "Файлы иконок (*.ico);;Все файлы (*.*)"
        )
        if file_path:
            self.IcoPathEdit.setText(file_path.replace("\\", "/"))

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
