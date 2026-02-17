import logging

from WorkProjectManager.AppData.schemas import MAIN_STRUCTURE_DATA, MAIN_DATA


class FileLoaderManager:
    """
        Загрузка, получение и сохранение данных по Главному Файлу
    """
    MAIN_FILE = "DataFile"
    MAIN_DATA = None

    def __init__(self, MainIFS):
        self.logger = logging.getLogger("FileLoaderManager")
        self.MainIFS = MainIFS

    def load_main_data(self):
        self.logger.info(f"[!!] - FileLoaderManager - load_main_data")
        self.MAIN_DATA = self.MainIFS.read_file(self.MAIN_FILE)
        if self.MAIN_DATA == {}:
            self.MAIN_DATA = MAIN_DATA

    def save_main_data(self):
        self.logger.info(f"[!!] - FileLoaderManager - save_main_data - Начинаем сохранение главных настроек...")
        if self.MainIFS.read_file(self.MAIN_FILE) == {} or self.MAIN_DATA != self.MainIFS.read_file(self.MAIN_FILE):
            self.logger.info(f"save_main_data = Условия выполнены, начинаю сохранение...")
            self.MainIFS.write_data(self.MAIN_FILE, self.MAIN_DATA)
        else:
            self.logger.info(f"save_main_data = Условия НЕ выполнены, завершение!")


class StructureFileLoaderManager(FileLoaderManager):
    """
        Загрузка, получение и сохранение данных по Структурному Файлу
    """
    MAIN_STRUCTURE_FILE = None
    MAIN_STRUCTURE_DATA = None
    MAIN_STRUCTURE_BACKUP_FILE = None

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def load_main_structure_file_name(self):
        self.MAIN_STRUCTURE_FILE = self.MAIN_DATA["MainStructureFile"]
        self.MAIN_STRUCTURE_BACKUP_FILE = self.MAIN_DATA["MainStructureBackUpFile"]

    def load_main_structure_data(self):
        self.MAIN_STRUCTURE_DATA = self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE)
        if self.MAIN_STRUCTURE_DATA == {}:
            self.MAIN_STRUCTURE_DATA = MAIN_STRUCTURE_DATA

    def save_main_structure_data(self):
        if self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE) == {}:
            self.MainIFS.write_data(self.MAIN_STRUCTURE_FILE, self.MAIN_STRUCTURE_DATA)
        elif self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE) != self.MAIN_STRUCTURE_DATA:
            self.MainIFS.write_data(self.MAIN_STRUCTURE_FILE, self.MAIN_STRUCTURE_DATA)

    def set_default_main_structure_data(self):
        self.MainIFS.write_data(self.MAIN_STRUCTURE_FILE, MAIN_STRUCTURE_DATA)

    def backup_main_structure_data(self):
        if self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE) != self.MAIN_STRUCTURE_DATA:
            self.MainIFS.write_data(self.MAIN_STRUCTURE_BACKUP_FILE, self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE))

    def import_main_structure_data(self, import_data: dict):
        self.backup_main_structure_data()
        if self.MainIFS.read_file(self.MAIN_STRUCTURE_FILE) != import_data and import_data != {}:
            self.MainIFS.write_data(self.MAIN_STRUCTURE_FILE, import_data)

    def delete_main_structure_data(self):
        self.MainIFS.write_data(self.MAIN_STRUCTURE_FILE, {})


class StructureChunksDataManager(StructureFileLoaderManager):
    """
        Загрузка и получение данных по Чанкам Данных
    """
    LIST_CHUNKS_DATA = None

    def __init__(self, MainIFS):
        super().__init__(MainIFS)

    def load_chunks_data(self):
        self.LIST_CHUNKS_DATA: list[dict] = self.MAIN_STRUCTURE_DATA["DataChunks"]

    def get_chunk_data(self, chunk_name: str) -> list[dict]:
        for iD, chunk in enumerate(self.LIST_CHUNKS_DATA):
            if list(chunk.keys())[0] == chunk_name:
                return self.LIST_CHUNKS_DATA[iD][chunk_name]
