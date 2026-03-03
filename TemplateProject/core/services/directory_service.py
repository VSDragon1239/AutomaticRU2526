# Основные операции над путями
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
import os
from pathlib import Path

# pip install pywin32
import win32con
import win32gui
from win32comext.shell import shell
import pythoncom
import win32com.client


class DirectoryService:
    def __init__(self, full_base_directory, starry_dir=False):
        logging.getLogger("DirectoryService")
        self.base_directory = full_base_directory.replace("\\", "/")
        if not os.path.exists(self.base_directory):
            if starry_dir:
                os.makedirs(self.base_directory, exist_ok=True)
            else:
                raise FileNotFoundError(f"Base directory not found: {self.base_directory}")

    def open_file(self, exe_name: str):
        """
        Запускает .exe, расположенный в base_directory, по его имени.
        """
        logging.info(f"[🚀] FileService - open_file - Старт: exe_name='{exe_name}'")
        logging.debug(f"[🔍] FileService - open_file - base_directory='{self.base_directory}'")

        # 1) Нормализация имени файла
        original_exe_name = exe_name
        if not exe_name.lower().endswith((".exe", ".lnk")):
            exe_name += ".exe"
            logging.debug(f"[✏️] FileService - open_file - Добавлено расширение: '{original_exe_name}' → '{exe_name}'")

        # 2) Построение пути
        exe_path = os.path.join(self.base_directory, exe_name).replace("\\", "/")
        logging.info(f"[📄] FileService - open_file - Итоговый путь: '{exe_path}'")

        # 3) Проверка существования файла
        if not os.path.isfile(exe_path):
            logging.error(f"[❌] FileService - open_file - Файл не найден: '{exe_path}'")
            # Логируем содержимое директории для отладки
            if os.path.isdir(self.base_directory):
                files = os.listdir(self.base_directory)
                logging.debug(
                    f"[📋] FileService - open_file - Файлы в base_directory: {files[:10]}{'...' if len(files) > 10 else ''}")
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        else:
            logging.debug(f"[✅] FileService - open_file - Файл существует, размер: {os.path.getsize(exe_path)} байт")

        try:
            # 4) Обработка ярлыков (.lnk)
            if exe_path.lower().endswith(".lnk"):
                logging.info(f"[🔗] FileService - open_file - Обработка ярлыка: '{exe_path}'")

                try:
                    pythoncom.CoInitialize()
                    logging.debug("[🔌] FileService - open_file - CoInitialize() выполнен")

                    shell_link = pythoncom.CoCreateInstance(
                        shell.CLSID_ShellLink, None,
                        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
                    )
                    logging.debug("[🔗] FileService - open_file - ShellLink создан")

                    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
                    logging.debug("[📁] FileService - open_file - IID_IPersistFile получен")

                    persist_file.Load(str(Path(exe_path)), 0)
                    logging.debug(f"[📥] FileService - open_file - Ярлык загружен: '{exe_path}'")

                    target_path, _ = shell_link.GetPath(shell.SLGP_UNCPRIORITY)
                    logging.info(f"[🎯] FileService - open_file - Цель ярлыка: '{target_path}'")

                except Exception as e:
                    logging.error(f"[❌] FileService - open_file - Ошибка при чтении ярлыка: {type(e).__name__}: {e}")
                    raise

                # 5) Проверка целевого пути ярлыка
                if not os.path.isfile(target_path):
                    logging.warning(f"[⚠️] FileService - open_file - Цель ярлыка не найдена: '{target_path}'")

                    old_drive = target_path[:2]
                    new_drive = os.path.splitdrive(self.base_directory)[0]
                    logging.debug(f"[🔄] FileService - open_file - Попытка замены диска: '{old_drive}' → '{new_drive}'")

                    if old_drive.upper() != new_drive.upper():
                        fixed_target = target_path.replace(old_drive, new_drive, 1)
                        logging.debug(f"[🔍] FileService - open_file - Проверка исправленного пути: '{fixed_target}'")

                        if os.path.isfile(fixed_target):
                            logging.info(
                                f"[✅] FileService - open_file - Путь исправлен: '{target_path}' → '{fixed_target}'")
                            target_path = fixed_target
                        else:
                            logging.error(
                                f"[❌] FileService - open_file - Исправленный путь тоже не найден: '{fixed_target}'")
                    else:
                        logging.debug(f"[ℹ️] FileService - open_file - Диски совпадают, замена не требуется")

                if not os.path.isfile(target_path):
                    logging.error(
                        f"[❌] FileService - open_file - Критическая ошибка: целевой файл ярлыка не найден: '{target_path}'")
                    raise FileNotFoundError(f"Target from shortcut not found: {target_path}")

                # 6) Запуск целевого файла из ярлыка
                cwd = os.path.dirname(target_path)
                logging.info(f"[🚀] FileService - open_file - Запуск через subprocess: '{target_path}', cwd='{cwd}'")
                try:
                    proc = subprocess.Popen([target_path], cwd=cwd)
                    logging.info(f"[✅] FileService - open_file - Процесс запущен, PID={proc.pid}")
                except Exception as e:
                    logging.error(f"[❌] FileService - open_file - Ошибка subprocess.Popen: {type(e).__name__}: {e}")
                    raise

            else:
                # 7) Запуск обычного .exe
                logging.info(f"[🚀] FileService - open_file - Запуск обычного exe через os.startfile: '{exe_path}'")
                try:
                    os.startfile(exe_path)
                    logging.info(f"[✅] FileService - open_file - os.startfile выполнен успешно")
                except Exception as e:
                    logging.error(f"[❌] FileService - open_file - Ошибка os.startfile: {type(e).__name__}: {e}")
                    raise

        except OSError as e:
            winerror = getattr(e, 'winerror', 0)
            if winerror == 1223:
                logging.warning(
                    f"[⚠️] FileService - open_file - Запуск отменён пользователем (ERROR_CANCELLED/1223): '{exe_path}'")
            else:
                logging.error(f"[❌] FileService - open_file - OSError (winerror={winerror}): {e}")
                raise
        except Exception as e:
            logging.error(f"[💥] FileService - open_file - Неожиданная ошибка: {type(e).__name__}: {e}")
            raise

        logging.info(f"[🏁] FileService - open_file - Успешное завершение, возвращаем путь: '{exe_path}'")
        return exe_path

    def open_full_path_file(self, exe_path: str):
        """
        Запускает .exe или .lnk по полному пути.
        Автоматически пробует расширения: (нет) -> .exe -> .lnk -> .exe.lnk
        """
        logging.info(f"[🚀] FileService - open_full_path_file - Старт: input='{exe_path}'")

        # 1) Список вариантов путей для проверки
        # Мы не меняем исходную строку сразу, а проверяем гипотезы
        possible_extensions = ["", ".exe", ".lnk", ".exe.lnk"]
        found_path = None

        # Очищаем путь от лишних слэшей для корректной проверки
        base_path = exe_path.strip().replace("\\", "/")

        # Если пользователь явно передал расширение, проверяем его в первую очередь
        lower_path = base_path.lower()
        if lower_path.endswith(".exe") or lower_path.endswith(".lnk"):
            # Если расширение уже есть, проверяем сначала как есть
            priorities = [base_path]
            # Добавляем .lnk только если сейчас .exe (случай "file.exe" -> "file.exe.lnk")
            if lower_path.endswith(".exe"):
                priorities.append(base_path + ".lnk")
        else:
            # Если расширения нет, перебираем все варианты
            priorities = [base_path + ext for ext in possible_extensions]

        # 2) Поиск существующего файла
        for path_variant in priorities:
            if os.path.isfile(path_variant):
                found_path = path_variant
                logging.debug(f"[✅] FileService - open_full_path_file - Найдено совпадение: '{found_path}'")
                break
            else:
                logging.debug(f"[🔍] FileService - open_full_path_file - Не найдено: '{path_variant}'")

        # 3) Если ничего не найдено
        if not found_path:
            logging.error(f"[❌] FileService - open_full_path_file - Файл не найден ни в одном из вариантов")
            # Логируем содержимое папки для отладки
            dir_path = os.path.dirname(base_path)
            if os.path.isdir(dir_path):
                files = os.listdir(dir_path)
                # Ищем похожие имена
                similar = [f for f in files if os.path.basename(base_path).split('.')[0] in f]
                if similar:
                    logging.warning(f"[💡] FileService - open_full_path_file - Похожие файлы в папке: {similar}")
            raise FileNotFoundError(f"Executable not found: {exe_path}")

        logging.info(f"[📄] FileService - open_full_path_file - Итоговый путь: '{found_path}'")

        try:
            # 4) Обработка ярлыков (.lnk)
            if found_path.lower().endswith(".lnk"):
                logging.info(f"[🔗] FileService - open_full_path_file - Обработка ярлыка: '{found_path}'")

                try:
                    pythoncom.CoInitialize()
                    shell_link = pythoncom.CoCreateInstance(
                        shell.CLSID_ShellLink, None,
                        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
                    )
                    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
                    persist_file.Load(str(Path(found_path)), 0)
                    target_path, _ = shell_link.GetPath(shell.SLGP_UNCPRIORITY)
                    logging.info(f"[🎯] FileService - open_full_path_file - Цель ярлыка: '{target_path}'")
                except Exception as e:
                    logging.error(
                        f"[❌] FileService - open_full_path_file - Ошибка чтения ярлыка: {type(e).__name__}: {e}")
                    raise

                # 5) Проверка и исправление пути ярлыка (смена диска)
                if not os.path.isfile(target_path):
                    logging.warning(f"[⚠️] FileService - open_full_path_file - Цель ярлыка не найдена: '{target_path}'")

                    old_drive = target_path[:2]
                    new_drive = os.path.splitdrive(found_path)[0]
                    logging.debug(
                        f"[🔄] FileService - open_full_path_file - Попытка замены диска: '{old_drive}' → '{new_drive}'")

                    if old_drive.upper() != new_drive.upper():
                        fixed_target = target_path.replace(old_drive, new_drive, 1)
                        if os.path.isfile(fixed_target):
                            logging.info(
                                f"[✅] FileService - open_full_path_file - Путь исправлен: '{target_path}' → '{fixed_target}'")
                            target_path = fixed_target
                        else:
                            logging.error(
                                f"[❌] FileService - open_full_path_file - Исправленный путь не найден: '{fixed_target}'")

                if not os.path.isfile(target_path):
                    logging.error(
                        f"[❌] FileService - open_full_path_file - Целевой файл ярлыка не найден: '{target_path}'")
                    raise FileNotFoundError(f"Target from shortcut not found: {target_path}")

                # 6) Запуск целевого файла
                cwd = os.path.dirname(target_path)
                logging.info(f"[🚀] FileService - open_full_path_file - Запуск: '{target_path}', cwd='{cwd}'")
                proc = subprocess.Popen([target_path], cwd=cwd)
                logging.info(f"[✅] FileService - open_full_path_file - Процесс запущен, PID={proc.pid}")

            else:
                # 7) Запуск обычного exe
                logging.info(f"[🚀] FileService - open_full_path_file - Запуск через os.startfile: '{found_path}'")
                os.startfile(found_path)
                logging.info(f"[✅] FileService - open_full_path_file - os.startfile выполнен")

        except OSError as e:
            winerror = getattr(e, 'winerror', 0)
            if winerror == 1223:
                logging.warning(f"[⚠️] FileService - open_full_path_file - Запуск отменён (1223): '{found_path}'")
            else:
                logging.error(f"[❌] FileService - open_full_path_file - OSError (winerror={winerror}): {e}")
                raise
        except Exception as e:
            logging.error(f"[💥] FileService - open_full_path_file - Неожиданная ошибка: {type(e).__name__}: {e}")
            raise

        logging.info(f"[🏁] FileService - open_full_path_file - Успешное завершение: '{found_path}'")
        return found_path

    def list_files(self, extension_filter: str | None = None, directory: str | None = None) -> list[str]:
        """
        Lists all files in the base directory (or in `directory` if задано),
        optionally filtering by file extension, и возвращает их в естественном
        (numeric) порядке, чтобы "1", "2", ..., "10", "11" шли правильно.
        """
        root = directory or self.base_directory
        files: list[str] = []

        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if not extension_filter or fn.lower().endswith(extension_filter.lower()):
                    files.append(os.path.join(dirpath, fn).replace("\\", "/"))

        # natural sort: разбиваем имя (без расширения) на текст и числа
        def natural_key(path: str):
            name = os.path.splitext(os.path.basename(path))[0]
            parts = re.split(r'(\d+)', name)
            return [
                int(part) if part.isdigit() else part.lower()
                for part in parts
            ]

        files.sort(key=natural_key)
        # print("list_files", files)
        return files

    def name_list_files(self, extension_filter=None):
        """
            Returns a list of file names (without paths) in the base directory,
            optionally filtering by file extension.
            """
        files = self.list_files(extension_filter)
        return [os.path.basename(file) for file in files]

    def create_directory(self, directory_name):
        """
        Creates a new directory inside the base directory.
        """
        new_directory = os.path.join(self.base_directory, directory_name).replace("\\", "/")
        os.makedirs(new_directory, exist_ok=True)
        return new_directory

    def delete_directory(self, directory_name, confirm=False):
        """
        Deletes a directory inside the base directory.
        """
        directory_path = os.path.join(self.base_directory, directory_name).replace("\\", "/")
        if os.path.exists(directory_path):
            print(self.list_files(directory=directory_path))
            if not self.list_files(directory=directory_path):
                shutil.rmtree(directory_path)
                return True
            else:
                if confirm:
                    user_yes = input(f"print Y, or Yes -> delete {directory_path, self.list_files}: ")
                    if user_yes.lower() == "y" or user_yes.lower() == "yes":
                        shutil.rmtree(directory_path)
                        return [True, 'Confirmation Required']
                else:
                    raise ValueError("Confirmation Required")
                    # return [False, 'Confirmation Required', [self.list_files(directory=directory_path)]]
        else:
            raise FileNotFoundError(f"Directory not found: {directory_path}")

    def move_file(self, source_file, target_directory, source_mode=False):
        """
        Moves a file to the target directory.
        :source_file: Путь задаётся абсолютно или относительно
        """
        if not source_mode:
            source_file = self.base_directory + '/' + source_file.replace("\\", "/")
            target_directory = self.base_directory + '/' + target_directory.replace("\\", "/")
        else:
            target_directory = target_directory.replace("\\", "/")
        if not os.path.exists(target_directory):
            raise FileNotFoundError(f"Target directory not found: {target_directory}")
        shutil.move(source_file, target_directory)

    def copy_file(
        self,
        source_file: str,
        target_directory: str,
        source_mode: bool = False,
        new_name: str | None = None
    ) -> str:
        """
        Копирует файл в target_directory. Если указан new_name — переименовывает файл при копировании.

        :param source_file: путь к исходному файлу (или относительный от base_directory)
        :param target_directory: папка, куда копировать (или относительный от base_directory)
        :param source_mode: если False — оба пути резолвятся относительно base_directory
        :param new_name: новое имя файла в целевой папке (например "config_backup.json")
        :return: абсолютный путь скопированного (и, возможно, переименованного) файла
        """
        # --- приводим пути к абсолютным ---
        if not source_mode:
            src = os.path.join(self.base_directory, source_file.replace("\\", "/"))
            dst_dir = os.path.join(self.base_directory, target_directory.replace("\\", "/"))
        else:
            src = source_file.replace("\\", "/")
            dst_dir = target_directory.replace("\\", "/")

        # проверяем, что источник есть
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Source file not found: {src}")

        # проверяем, что папка назначения есть
        if not os.path.isdir(dst_dir):
            raise FileNotFoundError(f"Target directory not found: {dst_dir}")

        # --- определяем имя итогового файла ---
        original_name = os.path.basename(src)
        final_name = new_name or original_name

        # полный путь до конечного файла
        dest_path = os.path.join(dst_dir, final_name)

        # копируем сразу под нужным именем
        shutil.copy(src, dest_path)

        return dest_path

    def create_shortcut(
            self,
            target_exe: str,
            target_directory: str,
            source_mode: bool = False,
            shortcut_name: str | None = None,
            arguments: str = "",
            working_directory: str | None = None,
            icon_location: str | None = None
    ) -> str:
        """
        Создаёт Windows‑ярлык (.lnk) на target_exe в папке target_directory.

        :param target_exe: путь к .exe (или относительный от base_directory)
        :param target_directory: папка, куда положить ярлык (или относит. от base_directory)
        :param source_mode: если False — пути резолвятся от base_directory
        :param shortcut_name: имя ярлыка (без .lnk); по умолчанию — имя .exe
        :param arguments: строка аргументов командной строки
        :param working_directory: рабочая папка для ярлыка (по умолчанию — папка exe)
        :param icon_location: путь к иконке (.ico) или None (тогда берётся сам .exe)
        :return: полный путь к созданному ярлыку
        """
        # --- резолвим пути аналогично copy_file ---
        if not source_mode:
            exe_path = os.path.join(self.base_directory, target_exe.replace("\\", "/"))
            dst_dir = os.path.join(self.base_directory, target_directory.replace("\\", "/"))
        else:
            exe_path = target_exe.replace("\\", "/")
            dst_dir = target_directory.replace("\\", "/")

        if not os.path.isfile(exe_path):
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        if not os.path.isdir(dst_dir):
            raise FileNotFoundError(f"Target directory not found: {dst_dir}")

        # Имя ярлыка
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]
        link_name = (shortcut_name or exe_name) + ".lnk"
        link_path = os.path.join(dst_dir, link_name)

        # Опционально рабочая папка
        work_dir = working_directory
        if work_dir is None:
            work_dir = os.path.dirname(exe_path)
        elif not source_mode:
            work_dir = os.path.join(self.base_directory, working_directory.replace("\\", "/"))
        work_dir = work_dir.replace("\\", "/")

        # Опционально иконка
        icon = icon_location or exe_path
        if not source_mode:
            icon = os.path.join(self.base_directory, icon.replace("\\", "/"))
        icon = icon.replace("\\", "/")
        if not os.path.isfile(icon):
            # можно просто проигнорировать, если нет
            icon = exe_path

        # --- создание ярлыка через COM ---
        pythoncom.CoInitialize()
        shell_link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
        )
        shell_link.SetPath(exe_path)
        shell_link.SetDescription(f"Shortcut to {exe_name}")
        if arguments:
            shell_link.SetArguments(arguments)
        shell_link.SetWorkingDirectory(work_dir)
        shell_link.SetIconLocation(icon, 0)

        # Query IPersistFile to save the .lnk file
        persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
        # Need Unicode for Windows
        persist_file.Save(str(Path(link_path)), 0)

        return link_path

    @staticmethod
    def rename_file(source_file_path: str, new_file_name: str) -> str:
        """
        Просто переименовывает уже существующий файл.

        :param source_file_path: полный путь к файлу
        :param new_file_name: новое имя (без пути)
        :return: новый полный путь
        """
        src = source_file_path.replace("\\", "/")
        if not os.path.isfile(src):
            raise FileNotFoundError(f"File to rename not found: {src}")

        dst = os.path.join(os.path.dirname(src), new_file_name)
        os.rename(src, dst)
        return dst

    def directory_exists(self, directory_name):
        """
        Checks if a directory exists in the base directory. (Если путь существует, возвращает True)
        """
        directory_path = os.path.join(self.base_directory, directory_name).replace("\\", "/")
        return os.path.exists(directory_path)

    def search_files(self, keyword):
        """
        Searches for files containing the specified keyword in their name.
        """
        result = []
        for root, _, filenames in os.walk(self.base_directory):
            for file in filenames:
                if keyword in file:
                    result.append(os.path.join(root, file).replace("\\", "/"))
        return result

    def get_directories(self):
        return [d for d in os.listdir(self.base_directory) if os.path.isdir(os.path.join(self.base_directory, d))]

    def move_directory_to_create_zip_file(self, target_directory, archive_name, archive_extension):
        """
        Обходит folder_path и упаковывает все файлы в archive_path.
        Сохраняет структуру вложенных папок.
        """

        target_directory = target_directory + f'/{archive_name}.{archive_extension}'
        print(target_directory)
        if os.path.exists(target_directory):
            raise FileExistsError(f"Archive already exists: {target_directory}")

        with zipfile.ZipFile(target_directory, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.base_directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Делаем относительный путь, чтобы не складывать абсолютные пути в архив
                    rel_path = os.path.relpath(full_path, start=self.base_directory)
                    zf.write(full_path, arcname=rel_path)

    def openFolder(self, sub_dir_name: str):
        logging.info(
            f"[📁] - DirectoryService - openFolder - Начало -> Открытие директории")

        logging.info(
            f"[📁] - DirectoryService - openFolder - Состав директорий -> {self.base_directory, sub_dir_name}")
        # 1) абсолютный путь
        folder_path = os.path.abspath(os.path.join(self.base_directory, sub_dir_name))
        logging.info(
            f"[📁] - DirectoryService - openFolder - Итоговая директория -> {folder_path}")
        logging.info(
            f"[📁] - DirectoryService - openFolder - Запуск сложного процесса COM и Shell")
        # 2) инициализируем COM и получаем интерфейс Shell
        try:
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("Shell.Application")
        except Exception as e:
            logging.error(f"[❌] Ошибка инициализации COM: {e}")
            return

        # 3) пробуем найти уже открытое окно на эту папку
        for win in shell.Windows():
            try:
                path = win.Document.Folder.Self.Path
            except Exception:
                continue
            if os.path.normcase(path) == os.path.normcase(folder_path):
                hwnd = win.HWND
                logging.info(f"[📁] Найдено открытое окно HWND: {hwnd}")
                # разворачиваем и ставим на передний план
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SetForegroundWindow(hwnd)
                return

        # 4) иначе открываем новую папку в том же процессе explorer.exe
        shell.Open(folder_path)

        # 5) ждём, пока окно появится, и снова ищем его среди Windows()
        time.sleep(0.5)
        for win in shell.Windows():
            try:
                path = win.Document.Folder.Self.Path
            except Exception as e:
                logging.debug(f"[⚠️] Пропуск окна при проверке: {e}")
                continue
            if os.path.normcase(path) == os.path.normcase(folder_path):
                hwnd = win.HWND
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SetForegroundWindow(hwnd)
                break
        logging.info(
            f"[✅📁] - DirectoryService - openFolder - Успешное завершение сложного процесса COM и Shell")

