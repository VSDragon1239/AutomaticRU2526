# Основные операции над файлами.
import csv
import json
import logging
import os
from json import JSONDecodeError

from TemplateProject.core.services.json_file_service import write_json_file_service


class FileService:
    """
    json
    """
    def __init__(self, full_directory: str, file_name: str, file_extension: str):
        self.logger = logging.getLogger("FileService")
        self.logger.info(f"[📁] - FileService - __init__ - Инициализация файлового сервиса: {full_directory, file_name, file_extension}")
        self.directory = full_directory.replace("\\", "/")
        self.file_name = file_name
        self.file_extension = file_extension
        self._file_path = os.path.join(self.directory, f"{self.file_name}.{self.file_extension}").replace("\\", "/")

        # if not os.path.exists(self._file_path):
        #     raise FileNotFoundError(f"File not found: {self._file_path}")

    def file_exists(self):
        """
        :return: True -> Если существует файл, иначе False
        """
        self.logger.info(f"[📁] - FileService - file_exists - Проверка существование файла...")
        if os.path.exists(self._file_path):
            return True
        return False

    def get_file_name(self):
        self.logger.info(f"[📁] - FileService - get_file_name - Получение названия файла...")
        return f"{self.file_name}"

    def get_file_extension(self):
        self.logger.info(f"[📁] - FileService - get_file_extension - Получение существование файла...")
        return f"{self.file_extension}"

    def get_file_path(self):
        self.logger.info(f"[📁] - FileService - get_file_path - Получение существование файла...")
        return self._file_path

    def get_path_to_file(self):
        self.logger.info(f"[📁] - FileService - get_path_to_file - Получение существование файла...")
        return self.directory

    def append_file(self, content):
        """
        Appends content to an existing file.
        """
        self.logger.info(f"[📁] - FileService - append_file - Добавление данных {content} в файл...")
        self.write_file(content, safeMode=True)

    def read_file(self, mode='r', encoding='utf-8'):
        self.logger.info(f"[📁] - FileService - read_file - Чтение файла...")
        with open(self._file_path, mode, encoding=encoding) as file:
            self.logger.info(f"[📁] - FileService - read_file - Проверка формата файла... {self.file_extension}")
            if self.file_extension == "json":
                try:
                    self.logger.info(f"[✅] - FileService - read_file - Чтение и закрытие json файла!")
                    value_json_file = json.load(file)
                    file.close()
                    return ['json', value_json_file]
                except JSONDecodeError as e:
                    self.logger.warning(f"[✅] - FileService - read_file - В json файле указаны не верные данные файла!")
                    print("В файле не верные данные:", e)
                    return ['json', file]

            elif self.file_extension == "zip":
                pass

            elif self.file_extension == "csv":
                value_csv_file = csv.reader(file)
                file.close()
                return ['csv', value_csv_file]
            elif self.file_extension == "xlsx":
                pass

            elif self.file_extension == "md":
                value_file = file.read()
                file.close()
                return ['markdown', value_file]
            else:
                file.close()
                return 'NOT_SUPPORTED'

    def create_file(self, content=None):
        """
        Creates a new file with the specified content. Content handling depends on the file type.
        """
        self.logger.info(f"[📁] - FileService - create_file - Создание файла...")
        self.logger.info(f"[📁] - FileService - create_file - Проверка наличия корректного пути для файла...")
        if os.path.exists(self._file_path):
            # Путь не найден куда вставлять файл
            raise FileExistsError(f"File already exists: {self._file_path}")
            # raise FileExistsError()

        self.logger.info(f"[📁] - FileService - create_file - Проверка пути для файла...")
        with open(self._file_path, 'w', encoding='utf-8') as file:
            self.logger.info(f"[📁] - FileService - create_file - Проверка формата файла {self.file_extension}...")
            if self.file_extension == "json":
                self.logger.info(f"[📁] - FileService - create_file - Проверка формата содержимого для json файла if(content == dict)...")
                if isinstance(content, dict):
                    json.dump(content, file, indent=4)
                    self.logger.info(f"[✅] - FileService - create_file - Файл успешно записан!")
                else:
                    raise ValueError("Content for JSON files must be a dictionary.")
            elif self.file_extension == "csv":
                if isinstance(content, list):
                    writer = csv.writer(file)
                    writer.writerows(content)
                else:
                    raise ValueError("Content for CSV files must be a list of lists.")
            elif self.file_extension in ["txt", "md"]:
                if isinstance(content, str):
                    file.write(content)
                else:
                    raise ValueError("Content for text files must be a string.")
            else:
                raise ValueError(f"File type '{self.file_extension}' is not supported.")

    def write_file(self, content, safeMode=False, ignore_value_type=False):
        """
        Writes new content to an existing file. Supports two modes:
        - Safe mode (safeMode=True): Appends new content to the existing content.
        - Default mode (safeMode=False): Completely overwrites the existing content.

        :param content: New content to write into the file.
        :param safeMode: If True, appends new content to the old one.
        :param ignore_value_type: If True, overwrites existing keys even if their types differ.
        """
        self.logger.info(f"[📁] - FileService - write_file - запись данных в файл с параметрами...")
        self.logger.info(f"[📁] - FileService - write_file - Параметры записи: {content, safeMode, ignore_value_type}")
        self.logger.info(f"[📁] - FileService - write_file - Проверка формата файла {self.file_extension}...")
        if self.file_extension == "json":
            self.logger.info(f"[📁][if[📁]else] - FileService - write_file - Проверка формата записываемых данных для json файла if(content == dict)...")
            if not isinstance(content, dict):
                self.logger.warn(f"[📁][if[!!]else] - FileService - write_file - Данные кривые, выдаём ошибку...")
                raise ValueError("Content for JSON files must be a dictionary.")
            self.logger.info(f"[📁][if[✅]else] - FileService - write_file - Проверка успешна пройдена!")

        self.logger.info(f"[if📁else] - FileService - write_file - Установка режима открытия файла if(safeMode==True): mode='a', else:'w'...")
        mode = 'a' if safeMode else 'w'
        self.logger.info(f"[📁] - FileService - write_file - Открытие файла...")
        with open(self._file_path, mode, encoding='utf-8') as file:
            self.logger.info(f"[📁] - FileService - write_file - Проверка формата файла {self.file_extension}...")
            if self.file_extension == "json":
                self.logger.info(f"[📁] - FileService - write_file - Начало записи данных через функцию (write_json_file_service)...")
                return write_json_file_service(file, self._file_path, content, safeMode, ignore_value_type)

            elif self.file_extension == "csv":
                if not isinstance(content, list):
                    raise ValueError("Content for CSV files must be a list of lists.")
                writer = csv.writer(file)
                if not safeMode:  # Full overwrite
                    writer.writerows(content)
                else:  # Append to existing content
                    for row in content:
                        writer.writerow(row)

            elif self.file_extension in ["txt", "md"]:
                if not isinstance(content, str):
                    raise ValueError("Content for text files must be a string.")
                if safeMode:
                    file.write(content)
                else:
                    file.write(content)  # Default behavior for 'w' mode
            else:
                raise ValueError(f"File type '{self.file_extension}' is not supported.")

    def delete_file(self):
        """
        Deletes the file at the specified path.
        """
        self.logger.info(f"[📁] - FileService - delete_file - Удаление файла если он существует...")
        if os.path.exists(self._file_path):
            os.remove(self._file_path)
            self.logger.info(f"[✅] - FileService - delete_file - Файл удалён!")
            return 1
        else:
            self.logger.info(f"[✅] - FileService - delete_file - Файл не найден!")
            raise FileNotFoundError(f"File not found: {self._file_path}")
