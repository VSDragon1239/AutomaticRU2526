from WorkUserInterfaceManager.App.InterfaceManager import InterfaceManager


def apiInterfaceService(iFSDirectory):
    InterfaceService = InterfaceManager(iFSDirectory)
    return InterfaceService
