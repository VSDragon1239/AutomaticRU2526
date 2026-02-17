from WorkProjectManager.App.FirstChunk import InterfaceGlobalProjectsDataManager, InterfaceGlobalProjectProjectsDataManager
from WorkProjectManager.App.SecondChunk import InterfaceApplicationsDataManager


class InterfaceFirstChunk(InterfaceGlobalProjectsDataManager, InterfaceGlobalProjectProjectsDataManager):
    def __init__(self, MainIFS):
        super().__init__(MainIFS)


class InterfaceSecondChunk(InterfaceApplicationsDataManager):
    def __init__(self, MainIFS):
        super().__init__(MainIFS)


class LastInterface(InterfaceFirstChunk, InterfaceSecondChunk):
    def __init__(self, MainIFS):
        super().__init__(MainIFS)


class InterfacesChunksLoader(LastInterface):
    def __init__(self, MainIFS):
        super().__init__(MainIFS)
