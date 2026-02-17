import os
import subprocess

from WorkUserInterfaceManager.settings import UI_FILES, UI_DIR


def compile_ui_files(source_dir, output_dir, logger):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.ui'):
                ui_file = os.path.join(root, file)
                py_file = os.path.join(output_dir, os.path.relpath(root, source_dir), file.replace('.ui', '.py'))
                py_file_dir = os.path.dirname(py_file)
                if not os.path.exists(py_file_dir):
                    os.makedirs(py_file_dir)
                subprocess.run(['pyside6-uic', ui_file, '-o', py_file])
                logger.info(
                    f'[✅][📁][↴] - compiled_files - compile_ui_files - Файл {ui_file} скомпилирован! -> {py_file}')
                # subprocess.run([sys.executable, '-m', 'PySide6.uic', ui_file, '-o', py_file], check=True)


def compiled_files(logger):
    logger.info('🡻][↴] - Manage - compiled_files - Компиляция интерфейса... - Метод compile_ui_files')
    for ui_file in UI_FILES:
        logger.info(f'[🡻][↺] - Manage - compiled_files - Компилируем все файлы... - Цикл for {ui_file} in {UI_FILES}')
        ui_src = os.path.join(UI_DIR)
        logger.info(
            f'[if⏳ else] - Manage - compiled_files - Условие -> Текущий путь {ui_src} существует? - {os.path.isdir(ui_src)}')
        if os.path.isdir(ui_src):
            logger.info(
                f'[if⏳ else] - Manage - compiled_files - Истина -> Вызываем метод compile_ui_files для обхода всех файлов и их последующей компиляции')
            compile_ui_files(ui_src, ui_src.replace("\\", "/"), logger)
            logger.info(
                f'[!if✅] - Manage - compiled_files - Истина -> Вызываем метод compile_ui_files для обхода всех файлов и их последующей компиляции')
    logger.info(f'[↺][✅] - Manage - compiled_files - Завершение -> все файлы скомпилированы и готовы к использованию!')
