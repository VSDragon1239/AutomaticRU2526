"""
Продвинутая система зеркалирования окон в MDI через Desktop Window Manager (DWM).
"""

import sys
import subprocess
import time
import threading
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMdiSubWindow, QMessageBox,
    QApplication, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, Slot
from PySide6.QtGui import QPainter, QImage, QPixmap, QResizeEvent

import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32process
import win32api

# Константы DWM API (из dwmapi.h)
DWM_TNP_RECTDESTINATION = 0x00000001
DWM_TNP_RECTSOURCE = 0x00000002
DWM_TNP_OPACITY = 0x00000004
DWM_TNP_VISIBLE = 0x00000008
DWM_TNP_SOURCECLIENTAREAONLY = 0x00000010


# Структуры для DWM API
class DWM_THUMBNAIL_PROPERTIES(ctypes.Structure):
    _fields_ = [
        ("dwFlags", wintypes.DWORD),
        ("rcDestination", wintypes.RECT),
        ("rcSource", wintypes.RECT),
        ("opacity", wintypes.BYTE),
        ("fVisible", wintypes.BOOL),
        ("fSourceClientAreaOnly", wintypes.BOOL)
    ]


class WindowMirrorWidget(QWidget):
    """Виджет, который зеркалирует окно другого приложения."""

    mirror_updated = Signal()  # Сигнал при обновлении зеркала
    window_closed = Signal(int)  # Сигнал при закрытии окна

    def __init__(self, target_hwnd: int, parent=None):
        """
        Args:
            target_hwnd: Handle окна для зеркалирования
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.target_hwnd = target_hwnd
        self.thumbnail_id = 0
        self.is_mirroring = False
        self.update_timer = QTimer()

        self._setup_ui()
        self._setup_mirror()
        self._setup_update_timer()

    def _setup_ui(self) -> None:
        """Настройка базового UI."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 150)

        # Фолбэк-лейбл (на случай ошибки зеркалирования)
        self.fallback_label = QLabel("Зеркалирование окна...", self)
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.hide()

    def _setup_mirror(self) -> None:
        """Настройка зеркалирования через DWM."""
        try:
            # Получаем функции DWM
            dwmapi = ctypes.windll.dwmapi

            # Создаем thumbnail
            thumbnail_id = wintypes.HANDLE()
            result = dwmapi.DwmRegisterThumbnail(
                int(self.winId()),
                self.target_hwnd,
                ctypes.byref(thumbnail_id)
            )

            if result == 0:  # S_OK
                self.thumbnail_id = thumbnail_id.value
                self.is_mirroring = True
                self._update_thumbnail_rect()
            else:
                self._fallback_to_screenshot_mode()

        except Exception as e:
            print(f"DWM mirroring failed: {e}")
            self._fallback_to_screenshot_mode()

    def _setup_update_timer(self) -> None:
        """Настройка таймера для обновления."""
        self.update_timer.timeout.connect(self._update_mirror)
        self.update_timer.start(16)  # ~60 FPS

    def _update_thumbnail_rect(self) -> None:
        """Обновление размера и позиции thumbnail."""
        if not self.is_mirroring or not self.thumbnail_id:
            return

        try:
            dwmapi = ctypes.windll.dwmapi
            props = DWM_THUMBNAIL_PROPERTIES()

            # Настраиваем свойства
            # props.dwFlags = DWM_TNP_RECTDESTINATION | DWM_TNP_VISIBLE
            props.fVisible = True
            props.fSourceClientAreaOnly = False

            # Устанавливаем размер под виджет
            rect = self.rect()
            props.rcDestination.left = 0
            props.rcDestination.top = 0
            props.rcDestination.right = rect.width()
            props.rcDestination.bottom = rect.height()

            # Обновляем thumbnail
            dwmapi.DwmUpdateThumbnailProperties(
                self.thumbnail_id,
                ctypes.byref(props)
            )

        except Exception as e:
            print(f"Failed to update thumbnail: {e}")

    def _fallback_to_screenshot_mode(self) -> None:
        """Фолбэк режим: периодические скриншоты окна."""
        self.is_mirroring = False
        self.fallback_label.show()

        # Устанавливаем более медленный таймер для скриншотов
        self.update_timer.stop()
        self.update_timer.timeout.connect(self._update_screenshot)
        self.update_timer.start(100)  # 10 FPS

    def _update_screenshot(self) -> None:
        """Обновление через скриншоты окна."""
        try:
            if not win32gui.IsWindow(self.target_hwnd):
                self.window_closed.emit(self.target_hwnd)
                return

            # Делаем скриншот окна
            import mss
            import mss.tools

            rect = win32gui.GetWindowRect(self.target_hwnd)

            with mss.mss() as sct:
                monitor = {
                    "left": rect[0],
                    "top": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                }

                screenshot = sct.grab(monitor)
                img = QImage(
                    screenshot.rgb,
                    screenshot.width,
                    screenshot.height,
                    QImage.Format_RGB888
                )

                self.fallback_label.setPixmap(QPixmap.fromImage(img.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )))

        except Exception as e:
            print(f"Screenshot failed: {e}")

    def _update_mirror(self) -> None:
        """Обновление зеркалирования."""
        if not win32gui.IsWindow(self.target_hwnd):
            self.window_closed.emit(self.target_hwnd)
            return

        if self.is_mirroring:
            self._update_thumbnail_rect()
        else:
            self._update_screenshot()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Обработка изменения размера."""
        super().resizeEvent(event)
        if self.is_mirroring:
            self._update_thumbnail_rect()

    def closeEvent(self, event) -> None:
        """Очистка ресурсов при закрытии."""
        if self.thumbnail_id:
            try:
                dwmapi = ctypes.windll.dwmapi
                dwmapi.DwmUnregisterThumbnail(self.thumbnail_id)
            except:
                pass

        self.update_timer.stop()
        event.accept()


class AppMirrorManager:
    """Менеджер для запуска и зеркалирования приложений."""

    def __init__(self):
        self.mirrored_windows: Dict[int, Dict] = {}  # hwnd -> info
        self.window_monitor_thread = None
        self.is_monitoring = False

    def launch_and_mirror(self, mdi_area, exe_path: str,
                          args: List[str] = None) -> Optional[QMdiSubWindow]:
        """
        Запускает приложение и создает зеркало в MDI.

        Args:
            mdi_area: MDI область
            exe_path: Путь к .exe
            args: Аргументы

        Returns:
            MDI окно с зеркалом или None
        """
        try:
            # Запускаем процесс
            process = subprocess.Popen(
                [exe_path] + (args or []),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

            # Ждем создание окна
            target_hwnd = self._wait_for_main_window(process.pid, timeout=10)
            if not target_hwnd:
                process.terminate()
                return None

            # Создаем MDI окно
            sub_window = QMdiSubWindow()
            sub_window.setWindowTitle(self._get_window_title(target_hwnd))
            sub_window.setAttribute(Qt.WA_DeleteOnClose)

            # Создаем виджет зеркалирования
            mirror_widget = WindowMirrorWidget(target_hwnd)
            sub_window.setWidget(mirror_widget)

            # Настраиваем обработчики
            mirror_widget.window_closed.connect(
                lambda hwnd: self._on_mirrored_window_closed(hwnd, sub_window)
            )

            sub_window.destroyed.connect(
                lambda: self._on_mdi_window_closed(target_hwnd)
            )

            # Сохраняем информацию
            self.mirrored_windows[target_hwnd] = {
                'process': process,
                'pid': process.pid,
                'sub_window': sub_window,
                'mirror_widget': mirror_widget,
                'exe_path': exe_path
            }

            # Добавляем в MDI
            mdi_area.addSubWindow(sub_window)
            sub_window.show()

            # Запускаем мониторинг окон, если еще не запущен
            self._start_window_monitor()

            return sub_window

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось запустить: {e}")
            return None

    def _wait_for_main_window(self, pid: int, timeout: int = 10) -> Optional[int]:
        """Ожидает создание главного окна процесса."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            hwnds = self._find_process_windows(pid)

            for hwnd in hwnds:
                # Ищем подходящее окно (видимое, с заголовком)
                if (win32gui.IsWindowVisible(hwnd) and
                        win32gui.GetWindowText(hwnd).strip()):
                    return hwnd

            time.sleep(0.1)

        return None

    def _find_process_windows(self, pid: int) -> List[int]:
        """Находит все окна процесса."""
        windows = []

        def enum_callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(enum_callback, windows)
        return windows

    def _get_window_title(self, hwnd: int) -> str:
        """Получает заголовок окна."""
        title = win32gui.GetWindowText(hwnd)
        return title if title else f"Приложение {hwnd}"

    def _start_window_monitor(self) -> None:
        """Запускает поток для мониторинга состояния окон."""
        if self.window_monitor_thread and self.window_monitor_thread.is_alive():
            return

        self.is_monitoring = True
        self.window_monitor_thread = threading.Thread(
            target=self._window_monitor_loop,
            daemon=True
        )
        self.window_monitor_thread.start()

    def _window_monitor_loop(self) -> None:
        """Цикл мониторинга окон."""
        while self.is_monitoring and self.mirrored_windows:
            hwnds_to_remove = []

            for hwnd, info in self.mirrored_windows.items():
                if not win32gui.IsWindow(hwnd):
                    # Окно закрыто - очищаем
                    hwnds_to_remove.append(hwnd)

                    # Закрываем MDI окно из главного потока
                    QTimer.singleShot(0, lambda h=hwnd: self._close_mdi_for_window(h))

            # Удаляем закрытые окна
            for hwnd in hwnds_to_remove:
                if hwnd in self.mirrored_windows:
                    del self.mirrored_windows[hwnd]

            time.sleep(0.5)  # Проверяем каждые 0.5 секунд

    @Slot(int)
    def _on_mirrored_window_closed(self, hwnd: int, sub_window: QMdiSubWindow) -> None:
        """Обработка закрытия зеркалируемого окна."""
        if hwnd in self.mirrored_windows:
            # Закрываем MDI окно
            sub_window.close()
            del self.mirrored_windows[hwnd]

    @Slot()
    def _on_mdi_window_closed(self, hwnd: int) -> None:
        """Обработка закрытия MDI окна."""
        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]

            # Закрываем приложение
            try:
                info['process'].terminate()

                # Даем время на корректное завершение
                try:
                    info['process'].wait(timeout=2)
                except subprocess.TimeoutExpired:
                    info['process'].kill()
            except:
                pass

            del self.mirrored_windows[hwnd]

    def _close_mdi_for_window(self, hwnd: int) -> None:
        """Закрывает MDI окно для указанного handle."""
        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]
            info['sub_window'].close()

    def close_all(self) -> None:
        """Закрывает все зеркалируемые приложения."""
        self.is_monitoring = False

        for hwnd, info in list(self.mirrored_windows.items()):
            self._on_mdi_window_closed(hwnd)
