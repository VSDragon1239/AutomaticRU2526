from WorkProjectManager.App.WorkChunksAndFiles import StructureChunksDataManager
from WorkProjectManager.AppData.schemas import APPLICATION_STRUCTURE_DATA


class StructureApplicationsDataManager(StructureChunksDataManager):
    """
        Загрузка и получение данных по Глобальным Проектам
    """
    applicationsList = list[dict]

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def load_applications_data(self) -> None:
        """
        Загружается во время инициализации
        :return: None
        """
        self.applicationsList: list[dict] = self.get_chunk_data("ApplicationsData")

    def get_application_data(self, applicationID: int) -> dict:
        for iD, application in enumerate(self.applicationsList):
            if str(application["ApplicationID"]) == str(applicationID):
                return {"indexApplication": iD, "dataApplication": application}
        raise KeyError("Не было найдено ни одного релевантного Приложения... / No Found Application...")

    def get_last_application_id(self) -> int:
        try:
            if len(self.applicationsList) == 0:
                return 0
            return int(self.applicationsList[-1]["ApplicationID"])
        except KeyError:
            raise KeyError("Загрузите Приложения перед тем как получать из него последний Проект")


class InterfaceApplicationsDataManager(StructureApplicationsDataManager):
    """
        Интерфейс для создания, редактирования и удаления данных по Приложениям
    """

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def new_application_data(self, applicationName: str, applicationType: str, applicationDescription: str, ApplicationAppPath: str, applicationIconPath: str):
        newData: dict = APPLICATION_STRUCTURE_DATA
        newData["ApplicationID"] = str(self.get_last_application_id() + 1)
        newData["ApplicationName"] = applicationName
        newData["ApplicationType"] = applicationType
        newData["ApplicationDescription"] = applicationDescription
        newData["ApplicationAppPath"] = ApplicationAppPath
        newData["ApplicationIconPath"] = applicationIconPath
        self.applicationsList.append(newData)

    def edit_application_data(self, applicationID: int, key: str, value: str):
        if key != "ApplicationID":
            editData: dict = self.get_application_data(applicationID)["dataApplication"]
            editData[key] = value
        else:
            raise ValueError("Ключ 'ApplicationID' запрещено редактировать!")

    def delete_application_data(self, applicationID: int):
        delData: dict = self.get_application_data(applicationID)
        self.applicationsList.pop(delData["indexApplication"])
