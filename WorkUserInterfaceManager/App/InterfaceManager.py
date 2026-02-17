import logging
import sys

from PySide6.QtWidgets import QApplication

from WorkProjectManager.api import apiProjectManager
from WorkUserInterfaceManager.App.MainInterface import MainInterface
from WorkUserInterfaceManager.App.MainQtInterface import UiMainWindow
from WorkUserInterfaceManager.App.Tools.LoggingCustom import get_logger_img
from WorkUserInterfaceManager.App.Tools.compile_ui_files import compiled_files


class InterfaceManager:
    App = None

    def __init__(self, iFSDirectory):
        """Основной класс запускаемой программы!"""
        self.logger = logging.getLogger("InterfaceManager")
        # compiled_files(self.logger)
        self.iPM = apiProjectManager(iFSDirectory)
        self.uIF = UiMainWindow
        self.MainInterface = MainInterface(self.iPM, self.uIF)

    def im_start(self):
        """Запускает главный цикл приложения"""
        self.logger.info(
            f"{get_logger_img('Запуск')} - InterfaceManager - im_start - Запускаем графический интерфейс приложения...")
        self.App = QApplication(sys.argv)
        self.MainInterface.start()
        sys.exit(self.App.exec())

    def im_stop(self):
        """Корректно останавливает приложение"""
        self.logger.info(
            f"{get_logger_img('Остановка')} - InterfaceManager - im_stop - Останавливаем графический интерфейс приложения...")
        self.MainInterface.stop()
        if self.App:
            self.App.exit(0)
            self.App = None
        else:
            sys.exit(0)

    def im_compile_interface_ui(self):
        self.logger.info(
            f"{get_logger_img('Запуск')} - InterfaceManager - im_compile_interface_ui - Запускаем компиляцию графического интерфейса...")
        compiled_files(self.logger)
