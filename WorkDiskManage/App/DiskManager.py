import logging

from WorkDiskManage.App.DeviceManager import DeviceManager
from WorkDiskManage.AppData.shemas import get_disks_schemas
from WorkJSONFiles.manage import apiFilesService


class DiskManager(DeviceManager):

    def __init__(self, storage_directory: str, storage_file: str = "DiskSettingsData"):
        """
            Получать все диски установленные в системе, выбрать нужные для работы.
            Установить главный диск для работы и остальные как зеркало.
            Также оставить некоторые, чтобы они не учитывались
        """
        super().__init__()
        self.FilesService = apiFilesService(storage_directory)
        self.logger = logging.getLogger(__name__)
        self.storage_file_name = storage_file

        self._build_letter_to_physical_map()
        self._fetch_drive_models()
        self._load_storage_file()

    def _load_storage_file(self):
        self.logger.info(f"📁 Загрузка файлового менеджера")
        if self.FilesService.read_file(self.storage_file_name) == {}:
            self.FilesService.write_data(self.storage_file_name, get_disks_schemas(self.get_drive()))
            self.logger.info(f"✅ Загрузка первичных данных завершена успешно!")
        self.logger.info(f"✅ Загрузка данных успешно завершена, возвращаем данные файла!")
        return self.FilesService.read_file(self.storage_file_name)

    def get_storage_file(self):
        return self.FilesService.read_file(self.storage_file_name)
