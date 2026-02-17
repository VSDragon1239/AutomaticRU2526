from WorkArchiveFiles.App.ArchiveDataManager import ArchiveDataManager
from WorkArchiveFiles.settings import FullTemplateDataDirectory, FullTestDirectory, Archive_type, Archive_password


def initArchiveManager(sources_directory, target_directory):
    """Инициализация ArchiveDataManager с готовыми путями."""
    return ArchiveDataManager(sources_directory, target_directory)


def TestingArchive():
    first_dir = input("Введите полный путь к директории, которую хотите заархивировать: ")
    last_dir = input("Введите полный путь к директории, куда кидать архив: ")
    password = input("Введите пароль (по умолчанию @<P@S5W0rD>):   ")
    manager = initArchiveManager(first_dir, last_dir)

    # Тест архивации с исключением временных папок
    if not password or "":
        password = Archive_password
    archive_path = manager.archive_data(
        archive_name="TestArchiveNameData",
        archive_type=Archive_type,
        archive_password=password,
        exclude_dirs=["__pycache__", "temp", "logs", "BackData", ".venv", ".obsidian"]
    )
    print(f"Создан архив: {archive_path}")


if __name__ == '__main__':
    TestingArchive()
# C:\(1)MyProgramms\WinRAR\WinRAR.exe
