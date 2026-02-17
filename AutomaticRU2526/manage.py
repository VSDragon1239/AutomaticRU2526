from AutomaticRU2526.settings import BASE_DIR
from WorkUserInterfaceManager.api import apiInterfaceService

if __name__ == '__main__':
    UserIF = apiInterfaceService(BASE_DIR)
    UserIF.im_start()
