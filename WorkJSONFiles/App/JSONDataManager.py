import logging
import os

from TemplateProject.core.services.file_service import FileService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class JSONDataManager:
    __OpenFile = None
    __load_data = None
    __filename = None

    def __init__(self, full_directory: str):
        self.logger = logging.getLogger("JSONDataManager")

        self.full_directory = full_directory
        if not os.path.exists(self.full_directory):
            # Если нет — создаём всю структуру директорий
            os.makedirs(self.full_directory, exist_ok=True)
            self.logger.info(f"[📁] - JSONDataManager - __open_file - Директория создана: {self.full_directory}")
        else:
            self.logger.info(f"✅ Директория существует: {self.full_directory}")

    def __open_file(self, filename):
        filename = filename.replace(".json", "")
        self.logger.info(f"[📁] - JSONDataManager - __open_file - Открываем файл с названием {filename}")
        self.logger.info(
            f"[if📁else] - JSONDataManager - __open_file - Условие - self.__OpenFile = {self.__OpenFile} is None or filename != {self.__filename}")
        if self.__OpenFile is None or filename != self.__filename:
            self.logger.info(f"[if📁else] - JSONDataManager - __open_file - Условие соблюдено!")
            self.__filename = filename
            self.logger.info(
                f"[if📁else] - JSONDataManager - __open_file - Текущие параметры открытия: {self.full_directory, self.__filename}")
            self.__OpenFile = FileService(full_directory=self.full_directory, file_name=self.__filename,
                                          file_extension="json")
            if not self.__OpenFile.file_exists():
                self.logger.info(f"[if📁else][if📁else] - JSONDataManager - __open_file - Файла не существует")
                self.logger.info(f"...Создаём пустой файл...")
                self.__OpenFile.create_file({})
                self.logger.info(
                    f"[✅][if📁else][if📁else] - JSONDataManager - __open_file - Файл {filename} успешно создан!")
            else:
                self.logger.info(f"[✅][if📁else][if📁else] - JSONDataManager - __open_file - Файл существует")
        else:
            self.logger.info(
                f"[if📁else] - JSONDataManager - __open_file - Файл {filename} уже открыт!")

    def __close_file(self):
        self.logger.info(f"[📁] - JSONDataManager - __close_file - Закрываем файл, стираем сохранённые данные...")
        self.__OpenFile = None
        self.__load_data = None
        self.__filename = None
        self.logger.info(f"[✅] - JSONDataManager - __close_file - Файл успешно закрыт, данные {self.__load_data} - стёрты!")

    def __safe_file(self, filename):
        filename = filename.replace(".json", "")
        self.logger.info(f"[📁] - JSONDataManager - __safe_file - Сохраняем файл {filename}...")
        cache_load_data = self.__load_data
        self.read_file(filename)
        cache_read_data = self.__load_data
        if cache_load_data != cache_read_data:
            self.__open_file(filename)
            self.__OpenFile.append_file(cache_load_data)
            self.read_file(filename)
            self.logger.info(f"[✅] - JSONDataManager - __safe_file - Данные сохранены, текущие данные: {self.__load_data}")
        self.logger.info(f"[✅] - JSONDataManager - __safe_file - Данные совпадают, сохранение не требуется.")

    def read_file(self, filename) -> dict:
        try:
            filename = filename.replace(".json", "")
        except AttributeError:
            filename = list(filename)[0].replace(".json", "")
        self.logger.info(f"[📁] - JSONDataManager - read_file - Читаем файл с названием {filename}")
        self.__open_file(filename)
        self.__load_data = self.__OpenFile.read_file()[1]
        self.logger.info(f"[✅] - JSONDataManager - read_file - Данные из файла успешно получены {self.__load_data}")
        return self.__load_data

    def write_data(self, filename, data):
        filename = filename.replace(".json", "")
        self.logger.info(f"[📁] - JSONDataManager - write_data - Записываем новые данные: {data}")
        self.__open_file(filename)
        self.__load_data = data
        self.__safe_file(filename)
        self.logger.info(f"[✅] - JSONDataManager - write_data - Запись прошла успешно! Новые данные: {self.__load_data}")

    def delete_file(self, filename):
        filename = filename.replace(".json", "")
        self.logger.info(f"[📁] - JSONDataManager - delete_file - Удаление файла {filename} ...")
        self.__open_file(filename)
        self.__OpenFile.delete_file()
        self.logger.info(f"[✅] - JSONDataManager - delete_file - Файл {filename} успешно удалён!")
        self.__close_file()
