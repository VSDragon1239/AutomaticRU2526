import logging

from TemplateProject.core.services.directory_service import DirectoryService
from WorkJSONFiles.api import apiFilesService
from WorkProjectManager.App.StructureManager import StructureManager
from WorkProjectManager.settings import FullTestDirectory, FullTemplateDataDirectory


class Manage:
    def __init__(self):
        self.logger = logging.getLogger("Manage")
        self.MainIFS = apiFilesService(FullTestDirectory)
        self.TemplateIFS = apiFilesService(FullTemplateDataDirectory)
        self.TemplateIDS = DirectoryService(FullTemplateDataDirectory)
        self.StructureReader = StructureManager(self.MainIFS)


if __name__ == '__main__':
    manage = Manage()
    # manage.logger.info(f" Просмотр результата get_structure(): {manage.StructureReader}")
    manage.logger.info(f" Просмотр результата load_all_data(): {manage.StructureReader.load_all_data()}")
    # manage.logger.info(f" Просмотр результата save(): {manage.StructureReader.save_all_data()}")
