import os
import subprocess
import zipfile
import logging
from datetime import datetime

from TemplateProject.core.services.directory_service import DirectoryService

# === Настройка логирования ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ArchiveDataManager:
    """
    Управляет архивированием данных из одной директории в другую.
    Можно исключать ненужные папки и файлы.
    """

    def __init__(self, source_directory: str, target_directory: str):
        self.source_dir = source_directory.replace("\\", "/")
        self.target_dir = target_directory.replace("\\", "/")

        self.source = DirectoryService(self.source_dir)
        self.target = DirectoryService(self.target_dir, starry_dir=True)

        # Настройка логгера
        self.logger = logging.getLogger("ArchiveDataManager")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(fmt)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def archive_data(
            self,
            archive_name: str,
            archive_type: str = "zip",
            archive_password: str | None = None,
            exclude_dirs: list[str] | None = None,
    ) -> str:
        """
        Архивирует директорию с возможностью задать пароль и тип архива.
        Поддерживаются ZIP (встроенно) и RAR5 (через WinRAR).
        """
        exclude_dirs = set(exclude_dirs or [])
        archive_type = archive_type.lower()

        self.logger.info(f"Начало архивирования: '{self.source_dir}' → '{self.target_dir}' ({archive_type.upper()})")

        if exclude_dirs:
            self.logger.info(f"Исключаем директории: {', '.join(exclude_dirs)}")

        os.makedirs(self.target_dir, exist_ok=True)
        archive_path = os.path.join(self.target_dir, f"{archive_name}.{archive_type}").replace("\\", "/")

        if os.path.exists(archive_path):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_path = os.path.join(self.target_dir, f"({archive_name})v{timestamp}.{archive_type}")
            self.logger.warning(f"⚠️ Архив '{archive_path}' уже существует, создаю новый: {backup_path}")
            archive_path = backup_path

        # ZIP архивирование
        if archive_type == "zip":
            self._create_zip_archive(archive_path, exclude_dirs, archive_password)

        # RAR архивирование через WinRAR
        elif archive_type in ("rar", "rar5"):
            self._create_rar_archive(archive_path, exclude_dirs, archive_password)

        else:
            raise ValueError(f"Неподдерживаемый тип архива: {archive_type}")

        self.logger.info(f"✅ Архив успешно создан: {archive_path}")
        return archive_path

    def _create_zip_archive(self, archive_path, exclude_dirs, archive_password):
        """Создание ZIP архива (встроенным zipfile)."""
        import pyzipper  # безопасный вариант с поддержкой AES и пароля
        try:
            with pyzipper.AESZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                if archive_password:
                    zf.setpassword(archive_password.encode("utf-8"))
                    zf.setencryption(pyzipper.WZ_AES, nbits=256)
                    self.logger.info("🔐 Установлен пароль на ZIP-архив")

                for root, dirs, files in os.walk(self.source_dir):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    rel_dir = os.path.relpath(root, start=self.source_dir)
                    if rel_dir != ".":
                        zf.writestr(rel_dir + "/", b"")
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=self.source_dir)
                        zf.write(full_path, arcname=rel_path)
        except Exception as e:
            self.logger.error(f"Ошибка создания ZIP архива: {e}")
            raise

    # ----------------------------------------------------------------------
    def _create_rar_archive(self, archive_path, exclude_dirs, archive_password):
        """Создание RAR5 архива через WinRAR CLI."""
        winrar_path = r"C:/(1)MyProgramms/WinRAR/WinRAR.exe"
        if not os.path.exists(winrar_path):
            winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
            if not os.path.exists(winrar_path):
                raise FileNotFoundError("WinRAR.exe не найден. Установите WinRAR и проверьте путь.")

        # Формируем список исключений
        exclude_args = []
        for ex in exclude_dirs:
            # *\folder_name\* — исключает эту папку в любом месте
            exclude_args += [f"-x*{ex}\\*"]

        cmd = [
                  winrar_path,
                  "a",  # добавить в архив
                  "-ep1",  # сохранять структуру без абсолютных путей
                  "-r",  # рекурсивно
                  "-ma5",  # формат RAR5
                  archive_path,
                  self.source_dir + "\\*",
              ] + exclude_args

        if archive_password:
            cmd.insert(2, f"-hp{archive_password}")  # защищает заголовки архива

        self.logger.info(f"Запуск WinRAR для создания RAR5 архива...")
        subprocess.run(cmd, check=True)
        self.logger.info("RAR5 архив успешно создан.")
