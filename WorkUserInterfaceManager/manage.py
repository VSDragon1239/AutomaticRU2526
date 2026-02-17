from WorkUserInterfaceManager.App.InterfaceManager import InterfaceManager
from WorkUserInterfaceManager.settings import BASE_DIR

if __name__ == '__main__':
    manage = InterfaceManager(BASE_DIR)
    manage.im_start()
