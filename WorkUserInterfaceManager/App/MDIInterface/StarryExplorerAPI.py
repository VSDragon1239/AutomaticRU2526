from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMdiSubWindow, QMessageBox,
    QApplication, QLabel, QSizePolicy, QMdiArea, QDockWidget, QStatusBar, QMainWindow
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, Slot
from PySide6.QtGui import QPainter, QImage, QPixmap, QResizeEvent, QAction

from WorkUserInterfaceManager.App.MDIInterface.StarryExplorer import AppMirrorManager
from WorkUserInterfaceManager.App.MDIInterface.StarryExplorerInterface import MirrorControlPanel


class FullscreenAppHost(QMainWindow):
    """
    Полноэкранное приложение-хост для зеркалирования окон.

    Особенности:
    - Полноэкранный режим без рамок (F11)
    - MDI интерфейс для управления окнами
    - Зеркалирование сторонних приложений
    """

    def __init__(self):
        super().__init__()

        # Менеджер зеркалирования
        self.mirror_manager = AppMirrorManager()

        # Настройка окна
        self._setup_window()
        self._setup_mdi_area()
        self._setup_menu()
        self._setup_control_panel()
        self._setup_status_bar()

        # Перехватчик горячих клавиш
        self._setup_hotkeys()

    def _setup_window(self) -> None:
        """Настройка главного окна."""
        self.setWindowTitle("Fullscreen App Host")

        # Начальный размер (можно потом развернуть на полный экран)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Стиль окна
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

    def _setup_mdi_area(self) -> None:
        """Настройка MDI области."""
        self.mdi_area = QMdiArea()
        self.mdi_area.setViewMode(QMdiArea.TabbedView)
        self.mdi_area.setDocumentMode(True)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)

        self.setCentralWidget(self.mdi_area)

    def _setup_menu(self) -> None:
        """Настройка меню."""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")

        new_app_action = QAction("Запустить приложение...", self)
        new_app_action.triggered.connect(self._show_launch_dialog)
        file_menu.addAction(new_app_action)

        file_menu.addSeparator()

        toggle_fullscreen_action = QAction("Полный экран (F11)", self)
        toggle_fullscreen_action.triggered.connect(self._toggle_fullscreen)
        file_menu.addAction(toggle_fullscreen_action)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Окно"
        window_menu = menubar.addMenu("Окно")

        cascade_action = QAction("Каскадом", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_action)

        tile_action = QAction("Рядом", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_action)

        close_all_action = QAction("Закрыть все", self)
        close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows)
        window_menu.addAction(close_all_action)

    def _setup_control_panel(self) -> None:
        """Настройка панели управления."""
        self.control_panel = MirrorControlPanel(
            self.mdi_area,
            self.mirror_manager
        )

        dock = QDockWidget("Управление приложениями", self)
        dock.setWidget(self.control_panel)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _setup_status_bar(self) -> None:
        """Настройка статус-бара."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Счетчик приложений
        self.app_counter_label = QLabel("Приложений: 0")
        self.status_bar.addPermanentWidget(self.app_counter_label)

        # Обновление счетчика
        self._update_app_counter()
        QTimer.singleShot(1000, self._update_app_counter)

    def _setup_hotkeys(self) -> None:
        """Настройка горячих клавиш."""
        # F11 - переключение полноэкранного режима
        from PySide6.QtGui import QKeySequence, QShortcut
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._toggle_fullscreen)

        # Ctrl+Q - выход
        exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        exit_shortcut.activated.connect(self.close)

    def _show_launch_dialog(self) -> None:
        """Показывает диалог запуска приложения."""
        # Можно использовать QDialog для более сложного интерфейса
        # Для простоты используем существующую панель
        pass

    def _toggle_fullscreen(self) -> None:
        """Переключение полноэкранного режима."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _update_app_counter(self) -> None:
        """Обновление счетчика приложений."""
        count = len(self.mdi_area.subWindowList())
        self.app_counter_label.setText(f"Приложений: {count}")

        # Обновляем каждую секунду
        QTimer.singleShot(1000, self._update_app_counter)

    def closeEvent(self, event) -> None:
        """Обработка закрытия приложения."""
        self.mirror_manager.close_all()
        event.accept()
