import logging
import os
import time
from functools import partial

from PySide6.QtCore import Qt, QDir, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QListWidgetItem, QWidget, QFileSystemModel, QTreeView, QFileIconProvider, \
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMenu, QInputDialog, QDialog

from WorkMouseDesign.api import WorkMouseDesignApi
from WorkUserInterfaceManager.App.DialogDataView import DialogDataView
from WorkUserInterfaceManager.App.MDIInterface.MDI_testing import ATestWindow
from WorkUserInterfaceManager.App.MDIInterface.ObsidianExplorer import ObsidianMirrorApp
from WorkUserInterfaceManager.App.MDIInterface.StarryExplorerAPI import FullscreenAppHost
from WorkUserInterfaceManager.App.Tools.LoggingCustom import get_logger_img
from WorkUserInterfaceManager.App.XMLFiles.main_window import Ui_QMW1
from WorkUserInterfaceManager.App.XMLFiles.test_mdi_window_ui import Ui_Form
from WorkUserInterfaceManager.App.XMLFiles.new_main_window import Ui_MainWindow
from WorkUserInterfaceManager.settings import icon_path


class UiMDIWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("UiMDIWindow")
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.logger.info(
            f"{get_logger_img('Инициализация')} - UiMDIWindow - __init__ - Инициализация иконки приложения... {icon_path}")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Тестовый виджет")


class UiMDIExplorerWindow(QTreeView):
    def __init__(self, path=QDir.currentPath()):
        super().__init__()
        self.logger = logging.getLogger("UiMDIExplorerWindow")

        # 1. Глубокая настройка модели
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setIconProvider(QFileIconProvider())
        self.model.setReadOnly(False)

        # self.setModel(self.model)
        # self.setRootIndex(self.model.index(path))

        # 2. Интерфейс управления (Навигация)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)

        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("←")
        self.address_bar = QLineEdit(path)

        nav_layout.addWidget(self.btn_back)
        nav_layout.addWidget(self.address_bar)
        self.layout.addLayout(nav_layout)

        # 3. Виджет отображения
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionMode(QTreeView.ExtendedSelection)
        self.layout.addWidget(self.tree)

        self.go_to_path(path)

        self.tree.doubleClicked.connect(self._on_item_double_clicked)
        self.address_bar.returnPressed.connect(lambda: self.go_to_path(self.address_bar.text()))
        self.btn_back.clicked.connect(self._go_up)

        # self.setColumnWidth(0, 250)
        # self.setAnimated(True)
        self.logger.info(
            f"{get_logger_img('Инициализация')} - UiMDIWindow - __init__ - Инициализация иконки приложения... {icon_path}")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Проводник")

    def go_to_path(self, path):
        """Глубокая установка индекса: проверяет существование и обновляет UI"""
        if os.path.exists(path):
            index = self.model.index(path)
            self.tree.setRootIndex(index)
            self.address_bar.setText(path)
            # Скрываем лишние колонки для чистоты (как в боковой панели)
            # self.tree.setColumnHidden(1, True)

    def _on_item_double_clicked(self, index):
        if self.model.isDir(index):
            new_path = self.model.filePath(index)
            self.go_to_path(new_path)
        else:
            # Здесь логика открытия файла
            import os
            os.startfile(self.model.filePath(index))

    def _go_up(self):
        """Переход на уровень выше"""
        current_path = self.model.filePath(self.tree.rootIndex())
        parent_path = os.path.dirname(current_path)
        if parent_path:
            self.go_to_path(parent_path)


class UiMainWindow(QMainWindow):
    listUpdateSelectGlobalProjectSignal = Signal(int)
    listUpdateSelectProjectSignal = Signal(int)

    listContextListWidgetCreateSignal = Signal(dict)
    listContextListWidgetEditSignal = Signal(dict)
    listContextListWidgetDeleteSignal = Signal(dict)

    widget_list_link = False

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("UiMainWindow")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger.info(
            f"{get_logger_img('Инициализация')} - UiMainWindow - __init__ - Инициализация MDI окна... {icon_path}")
        self.init_mdi_windows()
        self.logger.info(
            f"{get_logger_img('Инициализация')} - UiMainWindow - __init__ - Инициализация иконки приложения... {icon_path}")
        self.setWindowIcon(QIcon(icon_path))
        self.pet = WorkMouseDesignApi()

    def init_mdi_windows(self):
        self.ui.mdiArea.addSubWindow(UiMDIWindow())
        self.ui.mdiArea.addSubWindow(UiMDIExplorerWindow())
        # self.ui.mdiArea.addSubWindow(FullscreenAppHost())
        # self.ui.mdiArea.addSubWindow(ATestWindow())
        # self.ui.mdiArea.addSubWindow(ObsidianMirrorApp())

    def load_link_widget_list(self, widget_list):
        widget_list.itemClicked.disconnect(self.get_data_list_item)
        widget_list.itemClicked.connect(self.get_data_list_item)
        self.widget_list_link = True

    def set_items_to_widget_list(self, data_list, widget_list):
        self.logger.info(
            f"{get_logger_img('Загрузка')} - UiMainWindow - set_items_to_widget_list - Загрузка элементов из данных в список интерфейса: {data_list}")
        try:
            self.logger.info(
                f"{get_logger_img('Загрузка')} - UiMainWindow - set_items_to_widget_list - Перезагрузка подключения (itemClicked.disconnect/connect)...")
            self.load_link_widget_list(widget_list)
        except RuntimeError:
            self.logger.info(
                f"{get_logger_img('Загрузка')} - UiMainWindow - set_items_to_widget_list - Нет подключений! - RuntimeError")
            pass
        self.logger.info(
            f"{get_logger_img('Добавление')} - UiMainWindow - set_items_to_widget_list - Добавление data_list в widget... - {data_list}")
        for item_data in data_list:
            self.add_list_item(item_data, widget_list)
        self.logger.info(f"{get_logger_img('Возвращение')} - UiMainWindow - set_items_to_widget_list - Всё добавлено!")

    def add_list_item(self, item_data, widget_list, icon_path: str = None):
        self.logger.info(
            f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Добавление элемента в список: {item_data}")
        select_keys = list(item_data.keys())[0], list(item_data.keys())[1]
        item_text = f"{item_data.get(f'{select_keys[0]}')} - {item_data.get(f'{select_keys[1]}')}"
        self.logger.info(
            f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Условие - Добавление изображения: {icon_path}")
        if icon_path:
            self.logger.info(
                f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Истина - Добавление изображения: {icon_path}")
            icon = QIcon(icon_path)
            item = QListWidgetItem(icon, item_text)
        elif "ApplicationIconPath" in item_data.keys():
            self.logger.info(
                f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - ИначеЕсли - Добавление изображения: ApplicationIconPath - {item_data['ApplicationIconPath']}")
            icon = QIcon(item_data["ApplicationIconPath"])
            item = QListWidgetItem(icon, item_text)
        else:
            self.logger.info(f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Иначе - Без изображения")
            item = QListWidgetItem(item_text)
        self.logger.info(
            f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Добавление данных в элемент...")
        item.setData(Qt.UserRole, item_data)
        self.logger.info(f"{get_logger_img('Добавление')} - UiMainWindow - add_list_item - Добавление в интерфейс...")
        widget_list.addItem(item)

        self._setup_context_menu(
            widget_list)
        #     create_callback=lambda item, new_name: self.listContextListWidgetCreateSignal.emit({"item": item, "name": new_name}),
        #     rename_callback=lambda item, new_name: self.listContextListWidgetEditSignal.emit({"item": item, "name": new_name}),
        #     delete_callback=lambda item: self.listContextListWidgetDeleteSignal.emit({"item": item})
        # )

        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - add_list_item - Новый элемент был добавлен в список интерфейса!")

    def update_list_new_item(self, item_data, widget_list, icon_path: str = None):
        self.logger.info(
            f"{get_logger_img('Добавление')} - UiMainWindow - update_list_new_item - Обновление списка - добавление элемента: {item_data}")
        self.load_link_widget_list(widget_list)
        self.add_list_item(item_data, widget_list, icon_path)

    def get_data_list_item(self, item):
        self.logger.info(
            f"{get_logger_img('Получение')} - UiMainWindow - get_data_list_item - Получение данных: {item.data(Qt.UserRole)}")
        data: dict = item.data(Qt.UserRole)
        self.logger.info(
            f"{get_logger_img('Получение')} - UiMainWindow - get_data_list_item - Условие: GlobalProjectID in data.keys()")
        if "GlobalProjectID" in data.keys():
            self.logger.info(
                f"{get_logger_img('Получение')} - UiMainWindow - get_data_list_item - Истина - Посылаем сигнал listUpdateSelectSignal")
            self.listUpdateSelectGlobalProjectSignal.emit(int(data["GlobalProjectID"]))

        elif "ProjectID" in data.keys():
            self.logger.info(
                f"{get_logger_img('Получение')} - UiMainWindow - get_data_list_item - Истина - Посылаем сигнал listUpdateSelectSignal")
            self.listUpdateSelectProjectSignal.emit(int(data["ProjectID"]))

    def _setup_context_menu(self, widget_list):
        self.logger.info(
            f"{get_logger_img('Создание')} - UiMainWindow - _setup_context_menu - Создание контекстного меню - widget = {widget_list}")
        widget_list.setContextMenuPolicy(Qt.CustomContextMenu)
        widget_list.customContextMenuRequested.connect(
            partial(self._show_context_menu, widget_list)
        )

    def _show_context_menu(self, widget, pos):
        item = widget.itemAt(pos)
        if not item:
            menu = QMenu(widget)
            create_action = menu.addAction("Эксперимент")
            action = menu.exec(widget.viewport().mapToGlobal(pos))
            if action == create_action:
                new_item, ok = QInputDialog.getText(widget, "Эксперимент", "Экспериментальная функция:")
                if ok and new_item:
                    self.listContextListWidgetCreateSignal.emit({"item": item, "name": new_item})
            return

        menu = QMenu(widget)
        rename_action = menu.addAction("Переименовать")
        delete_action = menu.addAction("Удалить")
        action = menu.exec(widget.viewport().mapToGlobal(pos))

        if action == rename_action:
            dialog = QInputDialog(widget)
            dialog.setWindowTitle("Переименование1")
            dialog.setLabelText("Новое имя:")
            dialog.setTextValue(item.text())
            dialog.resize(500, 200)
            if dialog.exec() == QDialog.Accepted:
                new_name = dialog.textValue()
                self.listContextListWidgetEditSignal.emit({"item": item, "name": new_name})

            # new_name, ok = QInputDialog().getText(widget, "Переименование", "Новое имя:", text=item.text())
            # if ok and new_name:
            #     self.listContextListWidgetEditSignal.emit({"item": item, "name": new_name})
        elif action == delete_action:
            self.listContextListWidgetDeleteSignal.emit({"item": item})

    def get_dialog_data(self, data_title_name: str, count_data=1) -> list or None:
        self.logger.info(
            f"{get_logger_img('Открытие')} - UiMainWindow - get_dialog_data - Открытие диалога с {count_data} значениями...")
        data_list: list = DialogDataView(data_title_name, count_data, self).get_name()
        self.logger.info(
            f"{get_logger_img('Получение')} - UiMainWindow - get_dialog_data - Получение из диалога: {data_list}")
        if data_list:
            self.logger.info(
                f"{get_logger_img('Получение')} - UiMainWindow - get_dialog_data - Получение из диалога: {data_list}")
            return data_list
        self.logger.info(
            f"{get_logger_img('Создание')} - UiMainWindow - get_dialog_data - Создание проекта из диалога отменено")

    def get_global_projects_widget_list(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_global_projects_widget_list - Возвращение listWidget")
        return self.ui.listWidget

    def get_applications_widget_list(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_applications_widget_list - Возвращение listWidget_5")
        return self.ui.listWidget_5

    def get_projects_in_global_project_widget_list(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_projects_in_global_project_widget_list - Возвращение listWidget")
        return self.ui.listWidget_4

    def get_project_data_widget_list(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_project_data_widget_list - Возвращение listWidget_7")
        return self.ui.listWidget_7

    def get_button_global_projects_add(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_button_global_projects_add - Возвращение BTN11112")
        return self.ui.BTN11112

    def get_button_project_in_global_project_add(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_button_project_in_global_project_add - Возвращение BTN11114122_2")
        return self.ui.BTN11114122_2

    def get_button_start_project(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_button_start_project - Возвращение BTN11114122_2")
        return self.ui.BTN11114116

    def get_button_applications_add(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_button_applications_add - Возвращение BTN11111_2")
        return self.ui.BTN11111_2

    def get_button_save_data(self):
        self.logger.info(
            f"{get_logger_img('Возвращение')} - UiMainWindow - get_button_save_data - Возвращение BTN11114116_3")
        return self.ui.BTN11114116_3
