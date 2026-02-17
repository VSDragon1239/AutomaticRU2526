import logging

from PySide6.QtCore import Slot

from WorkUserInterfaceManager.App.MainInterfaceModel import MIModel
from WorkUserInterfaceManager.App.Tools.LoggingCustom import get_logger_img
from WorkUserInterfaceManager.App.Tools.system_tools import system_tool, system_tool_load
from WorkUserInterfaceManager.App.setupStyle.MainStyle import set_style_sheet
from WorkUserInterfaceManager.App.setupStyle.RandomTitle import set_random_title


class MainInterfaceView(MIModel):
    UiMainWindow = None

    def __init__(self, iPM, uIF):
        super().__init__(iPM, uIF)
        self.uIF = uIF

    def init_ui(self):
        self.UiMainWindow = self.uIF()
        self.UiMainWindow.showMaximized()

    def stop(self):
        self.UiMainWindow.close()
        self.UiMainWindow = None


class MainInterfaceViewModel(MainInterfaceView):
    def __init__(self, iPM, uIF):
        super().__init__(iPM, uIF)

    def vm_new_global_project(self):
        self.logger.info(f"[!!]  -  MainInterfaceViewModel  -  vm_new_global_project  -  : Создание проекта...")
        data_list: list = self.UiMainWindow.get_dialog_data("Глобальный Проект", count_data=2)
        if data_list is not None and len(data_list) == 2:
            self.new_global_projects_item(data_list[0], data_list[1])
            item_data = self.get_last_global_project_data()
            widget_list = self.UiMainWindow.get_global_projects_widget_list()
            self.UiMainWindow.update_list_new_item(item_data, widget_list)
            self.logger.info(f"[✅]  -  MainInterfaceViewModel  -  vm_new_global_project  -  : Новый проект создан!")
        else:
            raise IndexError("Создание проекта отменено!")

    def vm_new_project_in_global_project(self):
        self.logger.info(
            f"[!!]  -  MainInterfaceViewModel  -  vm_new_project_in_global_project  -  : Создание проекта...")
        data_list: list = self.UiMainWindow.get_dialog_data("Проект", count_data=3)
        if data_list is not None and len(data_list) == 3:
            self.new_project_in_global_project_item(data_list[0], data_list[1], data_list[2])
            item_data = self.get_last_project_in_global_project_data()
            widget_list = self.UiMainWindow.get_projects_in_global_project_widget_list()
            self.UiMainWindow.update_list_new_item(item_data, widget_list)
            self.logger.info(
                f"[✅]  -  MainInterfaceViewModel  -  vm_new_project_in_global_project  -  : Новый проект создан!")

    def vm_new_application(self):
        self.logger.info(f"[!!]  -  MainInterfaceViewModel  -  vm_new_application  -  : Добавление инструмента...")
        data_list: list = self.UiMainWindow.get_dialog_data("Приложение", count_data=5)
        self.logger.info(f"[if⏳else]  -  MainInterfaceViewModel  -  vm_new_application  - Условие {data_list}")
        if data_list is not None and len(data_list) == 5:
            self.logger.info(f"[if⏳else][!!]  -  MainInterfaceViewModel  -  vm_new_application  -  Истина - Установка путей")
            new_paths = system_tool("new_app", self.get_data_path("MainAppSystemLinksPath"), data_list[3], data_list[4])
            link_path = new_paths[0] + new_paths[1][0]
            icon_path = new_paths[0] + new_paths[1][1]

            item_data = self.new_applications_item(data_list[0], data_list[1], data_list[2], link_path, icon_path)
            widget_list = self.UiMainWindow.get_applications_widget_list()
            self.UiMainWindow.update_list_new_item(item_data, widget_list, icon_path=icon_path)
            self.logger.info(f"[✅]  -  MainInterfaceViewModel  -  vm_new_application  -  Новый инструмент создан!")
        else:
            raise IndexError("Произошла ошибка или добавление Приложения отменено!")


class MainInterfaceViewModelLinkData(MainInterfaceViewModel):
    def __init__(self, iPM, uIF):
        super().__init__(iPM, uIF)

    def link_model_data_to_interface_list(self):
        if self.get_global_projects_items_list() is not None:
            self.UiMainWindow.set_items_to_widget_list(self.get_global_projects_items_list(),
                                                       self.UiMainWindow.get_global_projects_widget_list())
        else:
            self.logger.warning(
                "[!🡻] - MainInterfaceViewModelLinkData  -  link_model_data_to_interface_list  -  Данные ещё НЕ загружены!!!")
            self.logger.info(
                "[!🡻] - MainInterfaceViewModelLinkData - link_model_data_to_interface_list - Чтение и загрузка данных...")
            self.load_data_from_model()

    def load_data_from_model(self):
        """
        Получение данных проектов и приложений из get_global_projects_items_list и загрузка их в
        set_items_to_widget_list() -> get_global_projects_widget_list
        :return:
        """
        self.load_all_data()
        self.logger.info(
            "[!🡻][✅] - MainInterfaceViewModelLinkData - load_data_from_model - Загрузка данных успешно завершена!")
        self.logger.info(
            "[if!!else] - MainInterfaceViewModelLinkData - load_data_from_model - Условие - get_global_projects_items_list")
        if self.get_global_projects_items_list():
            self.logger.info(
                "[🡻][if!!else] - MainInterfaceViewModelLinkData - load_data_from_model - Истина - Установка полученных ГП в виджет...")
            self.UiMainWindow.set_items_to_widget_list(self.get_global_projects_items_list(),
                                                       self.UiMainWindow.get_global_projects_widget_list())
            self.logger.info(
                "[✅][🡻][if!!else] - MainInterfaceViewModelLinkData - load_data_from_model - Установка завершена!")
        if self.get_applications_items_list():
            self.logger.info(
                "[🡻][if!!else] - MainInterfaceViewModelLinkData - load_data_from_model - Истина - Установка полученных Приложений в виджет...")
            self.UiMainWindow.set_items_to_widget_list(self.get_applications_items_list(),
                                                       self.UiMainWindow.get_applications_widget_list())

    @Slot(int)
    def load_projects_in_global_project_data_from_model(self, globalProjectID: int):
        """
        Получение данных из глобального проекта
        :return:
        """
        self.iPM.load_projects_data(globalProjectID)
        self.logger.info(
            "[if!!else] - MainInterfaceViewModelLinkData - load_projects_in_global_project_data_from_model - Условие - get_projects_in_global_project_items_list")
        if self.get_projects_in_global_project_items_list():
            widget = self.UiMainWindow.get_projects_in_global_project_widget_list()
            widget.clear()
            self.logger.info(
                "[🡻][if!!else] - MainInterfaceViewModelLinkData - load_projects_in_global_project_data_from_model - Истина - Установка полученных Проектов в виджет...")
            self.UiMainWindow.set_items_to_widget_list(self.get_projects_in_global_project_items_list(),
                                                       self.UiMainWindow.get_projects_in_global_project_widget_list())
            self.logger.info(
                "[✅][🡻][if!!else] - MainInterfaceViewModelLinkData - load_data_from_model - Установка завершена!")

    @Slot(int)
    def load_project_data(self, projectID: int):
        """
        Получение данных из проекта
        :return:
        """
        self.iPM.get_project_data(projectID)
        widget = self.UiMainWindow.get_project_data_widget_list()
        widget.clear()
        gp = self.iPM.currentGlobalProject
        gpp = self.iPM.currentProject
        list_data: list = system_tool_load("load_project", self.get_data_path("MainGlobalProjectsPath"), gp, gpp)
        self.UiMainWindow.set_items_to_widget_list(list_data, self.UiMainWindow.get_project_data_widget_list())

    def _start_project(self):
        self.logger.info(
            f"[!!]  -  MainInterfaceViewModel  -  vm_start_project  -  : Запуск проекта...")
        system_tool_load("start_project", self.get_data_path("MainGlobalProjectsPath"), self.iPM.currentGlobalProject, self.iPM.currentProject)

    def link_model_data_to_interface_button(self):
        self.logger.info(
            f"{get_logger_img('Загрузка')} - MainInterfaceViewModelLinkData - link_model_data_to_interface_button - Загрузка методов в кнопки...")
        self.UiMainWindow.get_button_global_projects_add().clicked.connect(self.vm_new_global_project)
        self.UiMainWindow.get_button_project_in_global_project_add().clicked.connect(
            self.vm_new_project_in_global_project)
        self.UiMainWindow.get_button_applications_add().clicked.connect(self.vm_new_application)
        self.UiMainWindow.get_button_save_data().clicked.connect(self.iPM.save_all_data)
        self.UiMainWindow.get_button_start_project().clicked.connect(self._start_project)

    def link_signals(self):
        """
        Пользовательские сигналы
        :return:
        """
        self.logger.info(
            f"{get_logger_img('Загрузка')} - MainInterfaceViewModelLinkData - link_signals - Загрузка пользовательских cигналов...")
        self.UiMainWindow.listUpdateSelectGlobalProjectSignal.connect(
            self.load_projects_in_global_project_data_from_model)
        self.UiMainWindow.listUpdateSelectProjectSignal.connect(self.load_project_data)
        self.UiMainWindow.listContextListWidgetCreateSignal.connect(lambda: self.logger.info("[✅] - MainInterfaceViewModelLinkData - link_signals - Вызов listContextListWidgetCreateSignal"))
        self.UiMainWindow.listContextListWidgetEditSignal.connect(lambda: self.logger.info("[✅] - MainInterfaceViewModelLinkData - link_signals - Вызов listContextListWidgetEditSignal"))
        self.UiMainWindow.listContextListWidgetDeleteSignal.connect(lambda: self.logger.info("[✅] - MainInterfaceViewModelLinkData - link_signals - Вызов listContextListWidgetDeleteSignal"))

    def all_links(self):
        self.logger.info(
            f"{get_logger_img('Загрузка')} - MainInterfaceViewModelLinkData - all_links - Загрузка данных интерфейса...")
        self.link_model_data_to_interface_list()
        self.link_model_data_to_interface_button()
        self.link_signals()


class MainInterface(MainInterfaceViewModelLinkData):
    def __init__(self, iPM, uIF):
        super().__init__(iPM, uIF)
        self.logger = logging.getLogger("MainInterface")

    def start(self):
        self.init_ui()
        self.all_links()
        self.setup_style()

    def setup_style(self):
        self.logger.info(f"{get_logger_img('Загрузка')} - MainInterface - setup_style - Установка стилей интерфейса")
        set_random_title(self.UiMainWindow, self.get_main_drive(), self.logger)
        set_style_sheet(self.UiMainWindow, self.logger)
