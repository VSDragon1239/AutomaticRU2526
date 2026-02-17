from WorkJSONFiles.App.JSONDataManager import JSONDataManager


def apiFilesService(Directory: str):
    JSONDataFiles = JSONDataManager(Directory)
    return JSONDataFiles
