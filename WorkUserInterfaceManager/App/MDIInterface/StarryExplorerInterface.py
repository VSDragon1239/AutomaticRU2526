"""
Упрощенный интерфейс для управления зеркалированием приложений.
"""
from pathlib import Path

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel,
    QGroupBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt


class MirrorControlPanel(QWidget):
    """Панель управления зеркалированием приложений."""

    def __init__(self, mdi_area, mirror_manager):
        super().__init__()
        self.mdi_area = mdi_area
        self.mirror_manager = mirror_manager

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Группа запуска
        launch_group = QGroupBox("Запуск приложения")
        launch_layout = QVBoxLayout()

        # Поле пути
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Путь к .exe...")
        self.browse_btn = QPushButton("Обзор")
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(self.browse_btn)
        launch_layout.addLayout(path_layout)

        # Поле аргументов
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Аргументы (через пробел)...")
        launch_layout.addWidget(self.args_edit)

        # Кнопка запуска
        self.launch_btn = QPushButton("Запустить и зеркалировать")
        launch_layout.addWidget(self.launch_btn)

        launch_group.setLayout(launch_layout)
        layout.addWidget(launch_group)

        # Список запущенных приложений
        self.apps_list = QListWidget()
        self.apps_list.setMaximumHeight(150)
        layout.addWidget(QLabel("Запущенные приложения:"))
        layout.addWidget(self.apps_list)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.focus_btn = QPushButton("Фокус")
        self.close_btn = QPushButton("Закрыть")
        self.close_all_btn = QPushButton("Закрыть все")

        btn_layout.addWidget(self.focus_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.close_all_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _setup_connections(self) -> None:
        """Настройка соединений."""
        self.browse_btn.clicked.connect(self._browse_exe)
        self.launch_btn.clicked.connect(self._launch_app)
        self.focus_btn.clicked.connect(self._focus_selected)
        self.close_btn.clicked.connect(self._close_selected)
        self.close_all_btn.clicked.connect(self._close_all)

    def _browse_exe(self) -> None:
        """Выбор файла .exe."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите приложение", "",
            "Executable files (*.exe);;All files (*.*)"
        )
        if file_path:
            self.path_edit.setText(file_path)

    def _launch_app(self) -> None:
        """Запуск приложения."""
        exe_path = self.path_edit.text().strip()
        if not exe_path:
            return

        args_text = self.args_edit.text().strip()
        args = args_text.split() if args_text else []

        # Запускаем приложение
        sub_window = self.mirror_manager.launch_and_mirror(
            self.mdi_area, exe_path, args
        )

        if sub_window:
            # Добавляем в список
            app_name = Path(exe_path).name
            item = QListWidgetItem(f"{app_name} ({sub_window.windowTitle()})")
            item.setData(Qt.UserRole, sub_window)
            self.apps_list.addItem(item)

            # Очищаем поля
            self.path_edit.clear()
            self.args_edit.clear()

    def _get_selected_subwindow(self):
        """Получает выбранное MDI окно."""
        items = self.apps_list.selectedItems()
        if not items:
            return None

        return items[0].data(Qt.UserRole)

    def _focus_selected(self) -> None:
        """Передает фокус выбранному приложению."""
        sub_window = self._get_selected_subwindow()
        if sub_window:
            sub_window.setFocus()

    def _close_selected(self) -> None:
        """Закрывает выбранное приложение."""
        sub_window = self._get_selected_subwindow()
        if sub_window:
            sub_window.close()

            # Удаляем из списка
            row = self.apps_list.row(self.apps_list.selectedItems()[0])
            self.apps_list.takeItem(row)

    def _close_all(self) -> None:
        """Закрывает все приложения."""
        self.mirror_manager.close_all()
        self.apps_list.clear()
