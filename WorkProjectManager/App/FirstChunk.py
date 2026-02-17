from WorkProjectManager.App.WorkChunksAndFiles import StructureChunksDataManager
from WorkProjectManager.AppData.schemas import GLOBAL_PROJECT_STRUCTURE_DATA, GLOBAL_PROJECT_PROJECT_STRUCTURE_DATA


class StructureGlobalProjectsDataManager(StructureChunksDataManager):
    """
        Загрузка и получение данных по Глобальным Проектам
    """
    GLOBAL_PROJECT_STRUCTURE_DATA = GLOBAL_PROJECT_STRUCTURE_DATA
    globalProjectsList = None

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def load_global_projects_data(self) -> dict or None:
        self.globalProjectsList: list[dict] = self.get_chunk_data("GlobalProjectsData")

    def get_global_project_data(self, globalProjectID: int) -> dict:
        """
        :param globalProjectID: int
        :return: {"indexGlobalProject": iD, "dataGlobalProject": globalProject}
        """
        for iD, globalProject in enumerate(self.globalProjectsList):
            if str(globalProject["GlobalProjectID"]) == str(globalProjectID):
                return {"indexGlobalProject": iD, "dataGlobalProject": globalProject}
        raise KeyError("Не был найден не один релевантный проект...")

    def get_last_global_project_id(self) -> int:
        try:
            if len(self.globalProjectsList) == 0:
                return 0
            return int(self.globalProjectsList[-1]["GlobalProjectID"])
        except KeyError:
            raise KeyError("Загрузите Глобальный Проект перед тем как получать из него последний Проект")


class InterfaceGlobalProjectsDataManager(StructureGlobalProjectsDataManager):
    """
        Интерфейс для создания, редактирования и удаления данных по Глобальным Проектам
    """

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def new_global_project_data(self, globalProjectName: str, globalProjectDescription: str):
        newData: dict = GLOBAL_PROJECT_STRUCTURE_DATA.copy()
        newData["GlobalProjectID"] = str(self.get_last_global_project_id() + 1)
        newData["GlobalProjectName"] = globalProjectName
        newData["GlobalProjectDescription"] = globalProjectDescription
        self.globalProjectsList.append(newData)

    def edit_global_project_data(self, globalProjectID: int, key: str, value: str):
        if key != "GlobalProjectProjectsData":
            if key != "GlobalProjectID":
                editData: dict = self.get_global_project_data(globalProjectID)["dataGlobalProject"]
                editData[key] = value
            else:
                raise ValueError("Ключ 'GlobalProjectID' запрещено редактировать!")
        else:
            raise ValueError("Значение ключа 'GlobalProjectProjectsData' запрещено редактировать на этом уровне")

    def delete_global_project_data(self, globalProjectID: int):
        delData: dict = self.get_global_project_data(globalProjectID)
        self.globalProjectsList.pop(delData["indexGlobalProject"])


class StructureGlobalProjectProjectsDataManager(StructureGlobalProjectsDataManager):
    """
        Загрузка и получение данных по Проектам из Глобальных Проектов
    """
    PROJECT_STRUCTURE_DATA = GLOBAL_PROJECT_PROJECT_STRUCTURE_DATA
    globalProjectProjectsList = list[dict]
    currentGlobalProject = int
    currentProject = int

    def __init__(self, MainIFS):
        super().__init__(MainIFS)


    def load_projects_data(self, globalProjectID: int):
        self.logger.info(f"[🡻] - StructureGlobalProjectProjectsDataManager - load_projects_data - Начало -> Получение данных проекта по globalProjectID")
        self.currentGlobalProject = globalProjectID
        self.globalProjectProjectsList: list[dict] = self.get_global_project_data(globalProjectID)[
            "dataGlobalProject"]["GlobalProjectProjectsData"]
        self.logger.info(f"[✅] - StructureGlobalProjectProjectsDataManager - load_projects_data - Данные загружены")

    def get_project_data(self, globalProjectProjectID: int) -> dict:
        self.logger.info(f"[🡻] - StructureGlobalProjectProjectsDataManager - get_project_data - Начало -> Получение данных проекта по globalProjectProjectID")
        for iD, globalProjectProject in enumerate(self.globalProjectProjectsList):
            self.logger.info(f"[🡻][if!!else] - StructureGlobalProjectProjectsDataManager - get_project_data - Условие -> str(globalProjectProject[ProjectID]) == str(globalProjectProjectID)")
            if str(globalProjectProject["ProjectID"]) == str(globalProjectProjectID):
                self.logger.info(f"[🡻][if!!else] - StructureGlobalProjectProjectsDataManager - get_project_data - Истина -> self.currentProject = globalProjectProjectID")
                self.currentProject = globalProjectProjectID
                self.logger.info(f"[✅][if!!else] - StructureGlobalProjectProjectsDataManager - get_project_data - Истина -> Возврат данных!")
                return {"indexGlobalProjectProject": iD, "dataGlobalProjectProject": globalProjectProject}
            self.logger.info(f"[🡻]... - StructureGlobalProjectProjectsDataManager - get_project_data - Продолжение или конец Цикла")
        self.logger.info(f"[✅] - StructureGlobalProjectProjectsDataManager - get_project_data - Конец, вызов ошибки!")
        raise KeyError("Не был найден не один релевантный проект...")

    def get_last_project_id(self) -> int:
        try:
            if len(self.globalProjectProjectsList) == 0:
                return 0
            return int(self.globalProjectProjectsList[-1]["ProjectID"])
        except KeyError:
            raise KeyError("Загрузите Глобальный Проект перед тем как получать из него последний Проект")


class InterfaceGlobalProjectProjectsDataManager(StructureGlobalProjectProjectsDataManager):
    """
        Интерфейс для создания, редактирования и удаления данных по Глобальным Проектам
    """

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def new_project_data(self, projectName: str, projectType: str, projectDescription: str):
        newData: dict = GLOBAL_PROJECT_PROJECT_STRUCTURE_DATA
        newData["ProjectID"] = str(self.get_last_project_id() + 1)
        newData["ProjectName"] = projectName
        newData["ProjectType"] = projectType
        newData["ProjectDescription"] = projectDescription
        self.globalProjectProjectsList.append(newData)

    def edit_project_data(self, ProjectID: int, key: str, value: str or dict or list[dict]):
        if key != "ProjectData":
            if key != "ProjectID":
                editData: dict = self.get_project_data(ProjectID)["dataGlobalProjectProject"]
                editData[key] = value
            else:
                raise ValueError("Ключ 'ProjectID' запрещено редактировать!")
        else:
            raise ValueError("Значение ключа 'ProjectData' запрещено редактировать на этом уровне")

    def delete_project_data(self, projectID: int):
        delData: dict = self.get_project_data(projectID)
        self.globalProjectProjectsList.pop(delData["indexGlobalProjectProject"])
