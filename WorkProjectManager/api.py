from WorkJSONFiles.api import apiFilesService
from WorkProjectManager.App.StructureManager import StructureManager


def apiProjectManager(iFSDirectory):
    MainIFS = apiFilesService(iFSDirectory)
    StructureReader = StructureManager(MainIFS)
    return StructureReader
