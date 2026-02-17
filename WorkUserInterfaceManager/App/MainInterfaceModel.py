import logging
from AutomaticRU2526.settings import BASE_DIR
from WorkProjectManager.App.StructureManager import StructureManager


class MIModelBase:
    def __init__(self, iPM):
        """
        Базовая модель для загрузки всех основных данных

        :param iPM: StructureManager()
        """
        self.logger = None
        self.iPM: StructureManager = iPM
        self._load_logger()

    def _load_logger(self):
        self.logger = logging.getLogger("MIModelBase")

    def load_all_data(self):
        self.logger.info(
            f"[🡻][↴] - MIModelBase  -   load_all_data - Загрузка всех основных данных - Метод load_all_data")
        self.iPM.load_all_data()


class MIModelMainSettingsData(MIModelBase):
    def __init__(self, iPM):
        """
        Начальная модель - Главные настройки.
        Также используется наследование базовой модели для возможности загрузки всех основных данных.
        Использует и получает данные из MAIN_DATA, также при необходимости сохраняет новые значения.

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def __get_path(self, path_type_key, default_path_setter):
        self.logger.info(
            f"[!!] - MIModelMainSettingsData - __get_path - Начало -> Получение {path_type_key, default_path_setter}")
        path_getter = self.iPM.MAIN_DATA[f"{path_type_key}"]
        if path_getter == "":
            self.logger.info(
                f"[if⏳else] - MIModelMainSettingsData - __get_path - Условие -> path_getter равен 'пустой строке'")
            path_setter = self.__set_default_path(path_type_key, path_getter, default_path_setter)
            self.logger.info(
                f"[✅] - MIModelMainSettingsData - __get_path - Результат -> path_setter равен '{self.iPM.MAIN_DATA[f'{path_type_key}']}'")
            return path_setter
        else:
            self.logger.info(
                f"[if⏳else] - MIModelMainSettingsData - __get_path - Иначе -> path_getter НЕ равен 'пустой строке'")
            self.logger.info(
                f"[✅] - MIModelMainSettingsData - __get_path - Результат -> path_getter равен '{self.iPM.MAIN_DATA[f'{path_type_key}']}'")
            return path_getter

    def __set_default_path(self, path_type_key, path_getter, default_path_setter):
        if path_getter == "":
            self.iPM.MAIN_DATA[f"{path_type_key}"] = default_path_setter
            return self.iPM.MAIN_DATA[f"{path_type_key}"]
        self.iPM.MAIN_DATA[f"{path_type_key}"] = path_getter
        return self.iPM.MAIN_DATA[f"{path_type_key}"]

    def _get_test_path(self):
        return self.iPM.MAIN_DATA["IfTestingPath"]

    def get_main_drive(self) -> str:
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - get_main_drive - Начало -> Получение Текущего пути к Главной Структуре -> MainDrive")
        return self.__get_path("MainDrive", str(BASE_DIR)[0:3])

    def get_structure_path(self) -> str:
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - get_structure_path - Начало -> Получение Текущего пути к Главной Структуре -> MainStructurePath")
        return self.__get_path("MainStructurePath", "1/")

    def _get_applications_path(self) -> str:
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - get_applications_path - Начало -> Получение Текущего пути к Главной Структуре -> MainApplicationsPath")
        return self.__get_path("MainApplicationsPath", "4/")

    def _get_app_installs_path(self) -> str:
        """Находится в пути, который складывается из get_main_drive + get_structure_path + get_applications_path"""
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - _get_app_installs_path - Начало -> Получение Текущего пути к Главной Структуре -> MainAppInstallsPath")
        return self.__get_path("MainAppInstallsPath", "1/")

    def _get_app_installing_path(self) -> str:
        """Находится в пути, который складывается из get_main_drive + get_structure_path + get_applications_path"""
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - _get_app_installing_path - Начало -> Получение Текущего пути к Главной Структуре -> MainAppInstallingPath")
        return self.__get_path("MainAppInstallingPath", "2/")

    def _get_app_portable_path(self) -> str:
        """Находится в пути, который складывается из get_main_drive + get_structure_path + get_applications_path"""
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - _get_app_portable_path - Начало -> Получение Текущего пути к Главной Структуре -> MainAppPortablePath")
        return self.__get_path("MainAppPortablePath", "3/")

    def _get_app_system_links_path(self) -> str:
        """Находится в пути, который складывается из get_main_drive + get_structure_path + get_applications_path"""
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - _get_app_system_links_path - Начало -> Получение Текущего пути к Главной Структуре -> MainAppSystemLinksPath")
        return self.__get_path("MainAppSystemLinksPath", "4/")

    def _get_global_projects_path(self) -> str:
        """Находится в пути, который складывается из get_main_drive + get_structure_path"""
        self.logger.info(
            f"[🡻] - MIModelMainSettingsData - get_app_installs_path - Начало -> Получение Текущего пути к Главной Структуре -> MainAppInstallsPath")
        return self.__get_path("MainGlobalProjectsPath", "1/")

    def get_data_path(self, path_type):
        structure_path = self.get_main_drive() + self.get_structure_path()
        if self._get_test_path():
            structure_path = str(BASE_DIR) + self.get_structure_path()
        else:
            self.logger.info(f"[🡻] - MIModelMainSettingsData - get_data_path - IF_TEST_STRUCTURE -> get_main_drive - NO WORK!!!")
            pass
            # structure_path = self.get_main_drive() + self.get_structure_path()
        match path_type:
            case "MainGlobalProjectsPath":
                return structure_path + self._get_global_projects_path()
            case "BackupsStructurePath":
                return structure_path + self._get_global_projects_path()
            case "MainApplicationsPath":
                return structure_path + self._get_applications_path()
            case "MainAppInstallsPath":
                return structure_path + self._get_app_installs_path()
            case "MainAppInstallingPath":
                return structure_path + self._get_app_installing_path()
            case "MainAppPortablePath":
                return structure_path + self._get_app_portable_path()
            case "MainAppSystemLinksPath":
                return structure_path + self._get_app_system_links_path()
            case _:
                raise ValueError("Не найдена директория в зарегистрированных путях")


class MIModelGlobalProjectManager(MIModelMainSettingsData):
    def __init__(self, iPM):
        """
        Начальная модель - Глобальные Проекты.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_global_projects_items_list(self) -> list:
        self.logger.info(
            f"[!🡵] - MIModelGlobalProjectManager - get_global_projects_items_list - Получение всех загруженных глобальных проектов - Список globalProjectsList")
        return self.iPM.globalProjectsList

    def get_last_global_project_data(self) -> dict:
        self.logger.info(
            f"[!🡵] - MIModelGlobalProjectManager - get_last_global_project_data - Получение последнего глобального проекта - Список[-1] globalProjectsList")
        return self.iPM.globalProjectsList[-1]

    def new_global_projects_item(self, name, description) -> int:
        self.logger.info(
            f"[!✲] - MIModelGlobalProjectManager - new_global_projects_item - Запись глобального проекта")
        self.iPM.new_global_project_data(name, description)
        self.logger.info(
            f"[!✲][✅] - MIModelGlobalProjectManager - new_global_projects_item - Проект успешно создан! - {self.iPM.globalProjectsList}")
        return self.iPM.get_last_global_project_id()


class MIModelProjectInGlobalProjectManager(MIModelGlobalProjectManager):
    def __init__(self, iPM):
        """
        Начальная модель - Проекты в Глобальном проекте.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def load_projects_data(self, globalProjectID: int):
        self.logger.info(f"[!🡵] - MIModelProjectInGlobalProjectManager - load_projects_data - Получение всех проектов")
        self.iPM.load_projects_data(globalProjectID)

    def get_projects_in_global_project_items_list(self) -> list:
        self.logger.info(
            f"[!🡵] - MIModelProjectInGlobalProjectManager - get_projects_in_global_project_items_list - Получение всех загруженных проектов - Список globalProjectProjectsList")
        return self.iPM.globalProjectProjectsList

    def get_last_project_in_global_project_data(self) -> dict:
        self.logger.info(
            f"[!🡵] - MIModelProjectInGlobalProjectManager - get_last_project_in_global_project_data - Получение последнего проекта - Список[-1] globalProjectProjectsList")
        return self.iPM.globalProjectProjectsList[-1]

    def new_project_in_global_project_item(self, name, project_type, description) -> int:
        self.logger.info(
            f"[!✲] - MIModelProjectInGlobalProjectManager - new_project_in_global_project_item - Запись проекта")
        self.iPM.new_project_data(name, project_type, description)
        self.logger.info(f"[!✲][✅] - MIModelProjectInGlobalProjectManager - new_project_in_global_project_item - Проект успешно создан! - {self.iPM.globalProjectProjectsList}")
        return self.iPM.get_last_project_id()


class MIModelApplicationManager(MIModelProjectInGlobalProjectManager):
    def __init__(self, iPM):
        """
        Начальная модель - Приложения.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_applications_items_list(self) -> list:
        return self.iPM.applicationsList

    def get_last_applications_data(self) -> dict:
        return self.iPM.applicationsList[-1]

    def new_applications_item(self, app_name, app_type, app_desc, app_path, icon_path) -> int:
        self.iPM.new_application_data(app_name, app_type, app_desc, app_path, icon_path)
        self.logger.info(f"[!✲][✅] - MIModelApplicationManager - new_applications_item - Приложение успешно зарегистрировано! - {self.iPM.globalProjectProjectsList}")
        return self.iPM.get_last_application_id()


class MIModelModulesManager(MIModelApplicationManager):
    def __init__(self, iPM):
        """
        Начальная модель - Модули.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_modules_items_list(self) -> list:
        pass

    def get_last_modules_data(self) -> dict:
        pass

    def new_modules_item(self, module_name, module_path) -> int:
        pass


class MIModelSubModuleManager(MIModelModulesManager):
    def __init__(self, iPM):
        """
        Начальная модель - ПодМодули.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_submodules_items_list(self) -> list:
        pass

    def get_last_submodules_data(self) -> dict:
        pass

    def new_submodules_item(self, module_name, module_path) -> int:
        pass


class MIModelSystemManager(MIModelSubModuleManager):
    def __init__(self, iPM):
        """
        Начальная модель - Система.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_system_items_list(self) -> list:
        pass

    def get_last_system_data(self) -> dict:
        pass

    def new_system_item(self, module_name, module_path) -> int:
        pass


class MIModelDrivesManager(MIModelSystemManager):
    def __init__(self, iPM):
        """
        Начальная модель - Система.
        Также используется наследование первой начальной модели для совмещения в одном классе

        :param iPM: StructureManager()
        """
        super().__init__(iPM)

    def get_system_items_list(self) -> list:
        pass

    def get_last_system_data(self) -> dict:
        pass

    def new_system_item(self, module_name, module_path) -> int:
        pass

    def remove_system_item(self, module_name, module_path) -> int:
        pass


class MIModel(MIModelDrivesManager):
    def __init__(self, iPM, uIF):
        """
        Последняя главная модель - объединяет все классы моделей разделённых по бизнес логике.
        Используется для наследования на следующий уровень -> ViewModel

        :param iPM: StructureManager()
        :param uIF: No Use Interface!!!
        """
        super().__init__(iPM)
        self.uIF = uIF
        self.uIF = None
