import logging

from TemplateProject.core.services.directory_service import DirectoryService
from WorkJSONFiles.api import apiFilesService
from WorkDataManager.App.StructureManager import StructureChunkDataReader
from WorkDataManager.settings import FullTestDirectory, FullTemplateDataDirectory


class Manage:
    def __init__(self):
        self.logger = logging.getLogger("Manage")
        self.MainIFS = apiFilesService(FullTestDirectory)
        self.TemplateIFS = apiFilesService(FullTemplateDataDirectory)
        self.TemplateIDS = DirectoryService(FullTemplateDataDirectory)
        self.StructureReader = StructureChunkDataReader(self.MainIFS, self.TemplateIFS, self.TemplateIDS)


if __name__ == '__main__':
    manage = Manage()
    manage.logger.info(f" Просмотр результата get_structure(): {manage.StructureReader.get_chunks_structure()}")
    manage.logger.info(f" Просмотр результата get_structure(): {manage.StructureReader.get_data_from_all_chunks()}")
