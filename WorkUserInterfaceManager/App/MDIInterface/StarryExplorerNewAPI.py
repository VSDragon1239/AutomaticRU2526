"""
Исправленная система зеркалирования окон с улучшенным отображением и поиском.
"""

import sys
import subprocess
import time
import threading
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMdiSubWindow, QMessageBox,
    QApplication, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QResizeEvent, QPainter, QBrush, QColor

import ctypes
from ctypes import wintypes
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        import win32process
        import win32api
        import win32com.client
        from win32comext.shell import shell
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
else:
    HAS_WIN32 = False
# ============================================================================
# DWM API КОНСТАНТЫ И СТРУКТУРЫ
# ============================================================================

# Константы DWM API
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


# ============================================================================
# УЛУЧШЕННЫЙ МЕНЕДЖЕР DWM THUMBNAIL
# ============================================================================

class DWMThumbnailManager:
    """Улучшенный менеджер для работы с DWM Thumbnails."""

    def __init__(self):
        self.dwmapi = ctypes.windll.dwmapi
        self._setup_prototypes()

    def _setup_prototypes(self):
        """Настройка прототипов функций для корректной работы."""
        # DwmRegisterThumbnail
        self.dwmapi.DwmRegisterThumbnail.argtypes = [
            ctypes.c_void_p,  # hwndDestination
            ctypes.c_void_p,  # hwndSource
            ctypes.POINTER(ctypes.c_ulonglong)  # phThumbnailId
        ]
        self.dwmapi.DwmRegisterThumbnail.restype = ctypes.c_long

        # DwmUpdateThumbnailProperties
        self.dwmapi.DwmUpdateThumbnailProperties.argtypes = [
            ctypes.c_ulonglong,  # hThumbnailId
            ctypes.POINTER(DWM_THUMBNAIL_PROPERTIES)  # ptnProperties
        ]
        self.dwmapi.DwmUpdateThumbnailProperties.restype = ctypes.c_long

        # DwmUnregisterThumbnail
        self.dwmapi.DwmUnregisterThumbnail.argtypes = [
            ctypes.c_ulonglong  # hThumbnailId
        ]
        self.dwmapi.DwmUnregisterThumbnail.restype = ctypes.c_long

    def register_thumbnail(self, dest_hwnd: int, source_hwnd: int) -> Optional[int]:
        """
        Регистрирует thumbnail для окна.

        Args:
            dest_hwnd: Handle окна-приемника
            source_hwnd: Handle окна-источника

        Returns:
            Thumbnail ID или None при ошибке
        """
        thumbnail_id = ctypes.c_ulonglong()

        result = self.dwmapi.DwmRegisterThumbnail(
            ctypes.c_void_p(dest_hwnd),
            ctypes.c_void_p(source_hwnd),
            ctypes.byref(thumbnail_id)
        )

        if result == 0:  # S_OK
            print(f"[DWM] Thumbnail создан успешно: {thumbnail_id.value}")
            return thumbnail_id.value
        else:
            print(f"[DWM] Ошибка создания thumbnail: 0x{result:08X}")
            return None

    def update_thumbnail_properties(self, thumbnail_id: int,
                                    rect: Tuple[int, int, int, int]) -> bool:
        """
        Обновляет свойства thumbnail.

        Args:
            thumbnail_id: ID thumbnail
            rect: (left, top, right, bottom) destination rectangle

        Returns:
            True если успешно, False если ошибка
        """
        try:
            props = DWM_THUMBNAIL_PROPERTIES()
            props.dwFlags = DWM_TNP_RECTDESTINATION | DWM_TNP_VISIBLE | DWM_TNP_SOURCECLIENTAREAONLY
            props.fVisible = True
            props.fSourceClientAreaOnly = True  # Только клиентская область

            # Устанавливаем целевой прямоугольник
            props.rcDestination.left = rect[0]
            props.rcDestination.top = rect[1]
            props.rcDestination.right = rect[2]
            props.rcDestination.bottom = rect[3]

            # Полный источник
            props.rcSource.left = 0
            props.rcSource.top = 0
            props.rcSource.right = 0x7FFFFFFF  # Максимальный размер
            props.rcSource.bottom = 0x7FFFFFFF

            result = self.dwmapi.DwmUpdateThumbnailProperties(
                ctypes.c_ulonglong(thumbnail_id),
                ctypes.byref(props)
            )

            if result != 0:
                print(f"[DWM] Ошибка обновления thumbnail: 0x{result:08X}")

            return result == 0
        except Exception as e:
            print(f"[DWM] Исключение при обновлении thumbnail: {e}")
            return False

    def unregister_thumbnail(self, thumbnail_id: int) -> bool:
        """
        Удаляет регистрацию thumbnail.

        Args:
            thumbnail_id: ID thumbnail

        Returns:
            True если успешно
        """
        try:
            result = self.dwmapi.DwmUnregisterThumbnail(
                ctypes.c_ulonglong(thumbnail_id)
            )
            return result == 0
        except Exception as e:
            print(f"[DWM] Ошибка удаления thumbnail: {e}")
            return False


# ============================================================================
# ВИДЖЕТ ДЛЯ ЗЕРКАЛИРОВАНИЯ ОКОН С УЛУЧШЕННЫМ ОТОБРАЖЕНИЕМ
# ============================================================================

class WindowMirrorWidget(QWidget):
    """Виджет для зеркалирования окна другого приложения."""

    # Сигналы
    window_closed = Signal(int)

    def __init__(self, target_hwnd: int, parent=None):
        """
        Args:
            target_hwnd: Handle окна для зеркалирования
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.target_hwnd = target_hwnd
        self.dwm_manager = DWMThumbnailManager()
        self.thumbnail_id = None
        self.is_mirroring = True
        self.update_timer = QTimer()
        self.last_screenshot = None

        self._setup_ui()
        self._setup_mirror()
        self._setup_update_timer()

    def _setup_ui(self) -> None:
        """Настройка базового UI."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 150)

        # Фолбэк-лейбл
        self.fallback_label = QLabel("Зеркалирование окна...", self)
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.hide()

        # Стиль
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
            }
            QLabel {
                color: #ccc;
                font-family: Consolas, monospace;
                padding: 10px;
            }
        """)

    def _setup_mirror(self) -> None:
        """Настройка зеркалирования через DWM."""
        try:
            # Пытаемся создать DWM thumbnail
            qt_hwnd = int(self.winId())
            print(f"[DWM] Создание thumbnail для окна {self.target_hwnd} в {qt_hwnd}")

            # Проверяем, что окно существует и видимо
            if not win32gui.IsWindow(self.target_hwnd):
                print(f"[DWM] Окно {self.target_hwnd} не существует")
                self._fallback_to_screenshot_mode()
                return

            # Пробуем активировать окно
            try:
                win32gui.SetForegroundWindow(self.target_hwnd)
            except:
                pass

            self.thumbnail_id = self.dwm_manager.register_thumbnail(
                qt_hwnd,
                self.target_hwnd
            )

            if self.thumbnail_id:
                self.is_mirroring = True
                print(f"[DWM] Thumbnail создан успешно, ID: {self.thumbnail_id}")

                # Даем DWM время на инициализацию
                QTimer.singleShot(100, self._update_thumbnail_rect)

                # Пробуем обновить сразу
                self._update_thumbnail_rect()
            else:
                print("[DWM] Не удалось создать thumbnail, переключаемся на скриншоты")
                self._fallback_to_screenshot_mode()

        except Exception as e:
            print(f"[DWM] Исключение при создании thumbnail: {e}")
            self._fallback_to_screenshot_mode()

    def _setup_update_timer(self) -> None:
        """Настройка таймера для обновления."""
        self.update_timer.timeout.connect(self._update_mirror)

        if self.is_mirroring:
            self.update_timer.start(100)  # 10 FPS для DWM
        else:
            self.update_timer.start(500)  # 2 FPS для скриншотов

    def _update_thumbnail_rect(self) -> None:
        """Обновление размера и позиции thumbnail."""
        if not self.is_mirroring or not self.thumbnail_id:
            return

        try:
            rect = self.rect()
            print(f"[DWM] Обновление thumbnail, размер: {rect.width()}x{rect.height()}")
            print(f"[DWM] Обновление thumbnail: {rect}")

            success = self.dwm_manager.update_thumbnail_properties(
                self.thumbnail_id,
                (0, 0, rect.width(), rect.height())
            )

            if success:
                print(f"[DWM] Thumbnail обновлен успешно")
                # Принудительная перерисовка
                self.update()
            else:
                print("[DWM] Не удалось обновить thumbnail")

        except Exception as e:
            print(f"[DWM] Ошибка обновления thumbnail: {e}")

    def _fallback_to_screenshot_mode(self) -> None:
        """Фолбэк режим: периодические скриншоты окна."""
        self.is_mirroring = False
        self.fallback_label.show()

        # Обновляем стиль для фолбэк режима
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 2px dashed #666;
            }
            QLabel {
                color: #888;
                font-family: Consolas, monospace;
                padding: 10px;
            }
        """)

        self.fallback_label.setText("Скриншот режим\n(Ожидание окна...)")
        print("[DWM] Переключен в режим скриншотов")

    def _capture_window_screenshot(self) -> Optional[QImage]:
        """Захватывает скриншот окна."""
        try:
            # Проверяем, существует ли окно
            if not win32gui.IsWindow(self.target_hwnd):
                return None

            # Получаем размеры и позицию окна
            rect = win32gui.GetWindowRect(self.target_hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            if width <= 0 or height <= 0:
                return None

            # Прямой захват через Windows API
            hdc_screen = win32gui.GetDC(0)
            hdc_mem = win32gui.CreateCompatibleDC(hdc_screen)
            hbitmap = win32gui.CreateCompatibleBitmap(hdc_screen, width, height)

            old_bitmap = win32gui.SelectObject(hdc_mem, hbitmap)

            # Копируем содержимое окна
            win32gui.BitBlt(
                hdc_mem, 0, 0, width, height,
                hdc_screen, rect[0], rect[1], win32con.SRCCOPY
            )

            # Восстанавливаем контекст
            win32gui.SelectObject(hdc_mem, old_bitmap)

            # Получаем информацию о bitmap
            bmpinfo = win32gui.GetObject(hbitmap)
            bmpstr = win32gui.GetBitmapBits(hbitmap, True)

            # Создаем QImage (обратите внимание на формат)
            # Для Windows скриншотов обычно используется BGR, а не RGB
            img = QImage(
                bmpstr,
                width,
                height,
                QImage.Format_ARGB32
            )

            # Конвертируем из BGR в RGB
            img = img.rgbSwapped()

            print("[ЗАХВАТ IMG]", hdc_screen, bmpstr, img)

            # Очистка ресурсов GDI
            win32gui.DeleteObject(hbitmap)
            win32gui.DeleteDC(hdc_mem)
            win32gui.ReleaseDC(0, hdc_screen)

            return img

        except Exception as e:
            print(f"[Screenshot] Ошибка захвата скриншота: {e}")
            return None

    def _update_screenshot(self) -> None:
        """Обновление через скриншоты окна."""
        try:
            # Проверяем, существует ли еще окно
            if not win32gui.IsWindow(self.target_hwnd):
                self.window_closed.emit(self.target_hwnd)
                self.fallback_label.setText("Окно закрыто")
                return

            # Захватываем скриншот
            img = self._capture_window_screenshot()

            if img is None:
                self.fallback_label.setText("Не удалось захватить окно")
                return

            # Сохраняем для возможного ресайза
            self.last_screenshot = img

            # Отображаем с сохранением пропорций
            pixmap = QPixmap.fromImage(img.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

            self.fallback_label.setPixmap(pixmap)
            self.fallback_label.setText("")  # Очищаем текст

        except Exception as e:
            print(f"[Screenshot] Исключение: {e}")
            self.fallback_label.setText(f"Ошибка: {str(e)}")

    def _update_mirror(self) -> None:
        """Обновление зеркалирования."""
        if not win32gui.IsWindow(self.target_hwnd):
            self.window_closed.emit(self.target_hwnd)
            return

        if self.is_mirroring:
            # Для DWM режима просто обновляем размер
            self._update_thumbnail_rect()
        else:
            self._update_screenshot()

    def paintEvent(self, event):
        """Переопределяем paintEvent для отладки."""
        super().paintEvent(event)

        # Для отладки: рисуем рамку
        if self.is_mirroring:
            painter = QPainter(self)
            painter.setPen(Qt.green)
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Обработка изменения размера."""
        super().resizeEvent(event)

        # Обновляем размер лейбла
        self.fallback_label.setGeometry(0, 0, self.width(), self.height())

        if self.is_mirroring:
            self._update_thumbnail_rect()
        elif self.last_screenshot is not None:
            # Обновляем размер скриншота
            pixmap = QPixmap.fromImage(self.last_screenshot.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            self.fallback_label.setPixmap(pixmap)

    def closeEvent(self, event) -> None:
        """Очистка ресурсов при закрытии."""
        if self.thumbnail_id:
            self.dwm_manager.unregister_thumbnail(self.thumbnail_id)
            self.thumbnail_id = None

        self.update_timer.stop()
        event.accept()


# ============================================================================
# УЛУЧШЕННЫЙ МЕНЕДЖЕР ЗЕРКАЛИРОВАНИЯ ПРИЛОЖЕНИЙ
# ============================================================================

class AppMirrorManager:
    """Улучшенный менеджер для запуска и зеркалирования приложений."""

    def __init__(self):
        self.mirrored_windows: Dict[int, Dict] = {}
        self.window_monitor_thread = None
        self.is_monitoring = False

    def find_standard_app(self, app_name: str) -> Optional[str]:
        """
        Поиск стандартных приложений Windows.

        Args:
            app_name: Имя приложения (notepad.exe, calc.exe, etc.)

        Returns:
            Полный путь к приложению или None
        """
        # Пути для поиска
        search_paths = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', app_name),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SysWOW64', app_name),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), app_name),
        ]

        # Для Windows 10/11 Calculator
        if app_name == "calc.exe":
            search_paths.extend([
                "C:\\Windows\\System32\\calc.exe",
                "C:\\Windows\\SysWOW64\\calc.exe",
                "C:\\Program Files\\WindowsApps\\*Calculator*\\Calculator.exe"
            ])

        for path in search_paths:
            if os.path.exists(path):
                print(f"[Find] Найдено {app_name} по пути: {path}")
                return path

        print(f"[Find] {app_name} не найден")
        return None

    def launch_and_mirror(self, mdi_area, exe_path: str,
                          args: List[str] = None,
                          wait_for_window: bool = True) -> Optional[QMdiSubWindow]:
        """
        Запускает приложение и создает зеркало в MDI.

        Args:
            mdi_area: MDI область
            exe_path: Путь к .exe
            args: Аргументы командной строки
            wait_for_window: Ждать ли появления окна

        Returns:
            MDI окно с зеркалом или None
        """
        try:
            # Проверяем существование файла
            if not Path(exe_path).exists():
                # Пробуем найти стандартное приложение
                app_name = os.path.basename(exe_path)
                found_path = self.find_standard_app(app_name)
                if found_path:
                    exe_path = found_path
                else:
                    raise FileNotFoundError(f"Файл не найден: {exe_path}")

            print(f"[Launch] Запуск: {exe_path}")

            # Запускаем процесс
            process_args = [exe_path]
            if args:
                process_args.extend(args)

            # Используем CREATE_NO_WINDOW для консольных приложений
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            process = subprocess.Popen(
                process_args,
                creationflags=creation_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            print(f"[Launch] Процесс запущен PID: {process.pid}")

            target_hwnd = None

            if wait_for_window:
                # Ждем создание главного окна
                target_hwnd = self._wait_for_main_window(process.pid, timeout=15)
                if not target_hwnd:
                    print(f"[Launch] Не удалось найти окно для PID {process.pid}")

                    # Пробуем найти любое окно процесса
                    target_hwnd = self._find_any_process_window(process.pid)

                    if not target_hwnd:
                        print(f"[Launch] Закрытие процесса без окна")
                        process.terminate()
                        return None
            else:
                # Не ждем окно, создаем пустой виджет
                target_hwnd = 0

            # Создаем MDI окно
            sub_window = QMdiSubWindow()

            if target_hwnd and target_hwnd != 0:
                title = self._get_window_title(target_hwnd)
                print(f"[Launch] Заголовок окна: {title}")
                sub_window.setWindowTitle(f"{title} (PID: {process.pid})")
            else:
                sub_window.setWindowTitle(f"{Path(exe_path).name} (PID: {process.pid})")

            sub_window.setAttribute(Qt.WA_DeleteOnClose)

            # Создаем виджет зеркалирования
            if target_hwnd and target_hwnd != 0:
                mirror_widget = WindowMirrorWidget(target_hwnd)
            else:
                # Создаем заглушку
                mirror_widget = QLabel(f"Приложение запущено\nPID: {process.pid}")
                mirror_widget.setAlignment(Qt.AlignCenter)

            sub_window.setWidget(mirror_widget)

            # Настраиваем обработчики
            if hasattr(mirror_widget, 'window_closed'):
                mirror_widget.window_closed.connect(
                    lambda hwnd: self._on_mirrored_window_closed(hwnd, sub_window)
                )

            sub_window.destroyed.connect(
                lambda: self._on_mdi_window_closed(target_hwnd if target_hwnd else 0)
            )

            # Сохраняем информацию
            self.mirrored_windows[target_hwnd if target_hwnd else 0] = {
                'process': process,
                'pid': process.pid,
                'sub_window': sub_window,
                'mirror_widget': mirror_widget,
                'exe_path': exe_path,
                'has_window': bool(target_hwnd and target_hwnd != 0)
            }

            # Добавляем в MDI область
            mdi_area.addSubWindow(sub_window)
            sub_window.show()

            # Запускаем мониторинг окон
            self._start_window_monitor()

            print(f"[Launch] Приложение успешно зеркалировано")
            return sub_window

        except Exception as e:
            print(f"[Launch] Ошибка: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось запустить: {e}")
            return None

    def _wait_for_main_window(self, pid: int, timeout: int = 15) -> Optional[int]:
        """Ожидает создание главного окна процесса."""
        start_time = time.time()
        last_check = 0

        print(f"[Wait] Ожидание окна для PID {pid} (таймаут: {timeout} сек)...")

        while time.time() - start_time < timeout:
            hwnds = self._find_process_windows(pid)

            if hwnds:
                print(f"[Wait] Найдено окон: {len(hwnds)}")

                for i, hwnd in enumerate(hwnds):
                    title = win32gui.GetWindowText(hwnd)
                    visible = win32gui.IsWindowVisible(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]

                    print(f"[Wait] Окно {i + 1}: hwnd={hwnd}, title='{title}', "
                          f"visible={visible}, size={width}x{height}")

                    # Берем первое подходящее окно
                    if visible and title and width > 10 and height > 10:
                        print(f"[Wait] Выбрано окно: {hwnd}")
                        return hwnd

            # Логируем каждые 3 секунды
            if time.time() - last_check > 3:
                print(f"[Wait] Все еще ожидаю окно для PID {pid}...")
                last_check = time.time()

            time.sleep(0.5)

        print(f"[Wait] Таймаут ожидания окна для PID {pid}")
        return None

    def _find_any_process_window(self, pid: int) -> Optional[int]:
        """Находит любое окно процесса без требований."""
        hwnds = self._find_process_windows(pid)

        if hwnds:
            # Возвращаем первое окно
            return hwnds[0]

        return None

    def _find_process_windows(self, pid: int) -> List[int]:
        """Находит все окна процесса."""
        windows = []

        def enum_callback(hwnd, hwnds):
            if win32gui.IsWindow(hwnd):
                try:
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        hwnds.append(hwnd)
                except:
                    pass
            return True

        try:
            win32gui.EnumWindows(enum_callback, windows)
        except Exception as e:
            print(f"[Find] Ошибка перечисления окон: {e}")

        return windows

    def _get_window_title(self, hwnd: int) -> str:
        """Получает заголовок окна."""
        try:
            title = win32gui.GetWindowText(hwnd)
            return title if title else f"Окно {hwnd}"
        except:
            return f"Окно {hwnd}"

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
        print("[Monitor] Мониторинг окон запущен")

    def _window_monitor_loop(self) -> None:
        """Цикл мониторинга окон."""
        while self.is_monitoring and self.mirrored_windows:
            hwnds_to_remove = []

            for hwnd, info in self.mirrored_windows.items():
                # Для оконных приложений проверяем существование окна
                if info.get('has_window', False) and hwnd != 0:
                    if not win32gui.IsWindow(hwnd):
                        hwnds_to_remove.append(hwnd)
                        print(f"[Monitor] Окно {hwnd} закрыто")

                # Проверяем состояние процесса
                process = info['process']
                if process.poll() is not None:
                    hwnds_to_remove.append(hwnd)
                    print(f"[Monitor] Процесс {process.pid} завершен")

            # Удаляем закрытые окна/процессы
            for hwnd in hwnds_to_remove:
                if hwnd in self.mirrored_windows:
                    QTimer.singleShot(0, lambda h=hwnd: self._close_mdi_for_window(h))

            time.sleep(1)

    @Slot(int)
    def _on_mirrored_window_closed(self, hwnd: int, sub_window: QMdiSubWindow) -> None:
        """Обработка закрытия зеркалируемого окна."""
        print(f"[Event] Зеркалируемое окно закрылось: {hwnd}")

        if hwnd in self.mirrored_windows:
            # Закрываем MDI окно
            sub_window.close()

    @Slot()
    def _on_mdi_window_closed(self, hwnd: int) -> None:
        """Обработка закрытия MDI окна."""
        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]
            print(f"[Event] Закрытие процесса для окна {hwnd} (PID: {info['pid']})")

            try:
                process = info['process']

                # Пытаемся закрыть корректно
                if process.poll() is None:
                    # Сначала WM_CLOSE для GUI окон
                    if hwnd != 0 and win32gui.IsWindow(hwnd):
                        try:
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            time.sleep(0.5)
                        except:
                            pass

                    # Terminate если еще жив
                    if process.poll() is None:
                        process.terminate()

                        # Ждем завершения
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            process.kill()

            except Exception as e:
                print(f"[Event] Ошибка при закрытии процесса: {e}")

            del self.mirrored_windows[hwnd]

    def _close_mdi_for_window(self, hwnd: int) -> None:
        """Закрывает MDI окно для указанного handle."""
        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]
            info['sub_window'].close()

    def close_all(self) -> None:
        """Закрывает все зеркалируемые приложения."""
        self.is_monitoring = False

        print("[Manager] Закрытие всех приложений...")

        for hwnd, info in list(self.mirrored_windows.items()):
            self._on_mdi_window_closed(hwnd)


# ============================================================================
# ТЕСТОВЫЙ ИНТЕРФЕЙС С УЛУЧШЕННОЙ ОБРАБОТКОЙ
# ============================================================================

if __name__ == "__main__":
    """Тестовое приложение для зеркалирования окон."""

    from PySide6.QtWidgets import (
        QMainWindow, QMdiArea, QPushButton, QVBoxLayout,
        QWidget, QHBoxLayout, QFileDialog, QLineEdit,
        QGroupBox, QComboBox, QCheckBox
    )


    class ATestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.mirror_manager = AppMirrorManager()

            self._setup_ui()
            self.setWindowTitle("Window Mirroring Test - Fixed")
            self.resize(1200, 800)

        def _setup_ui(self):
            central = QWidget()
            layout = QVBoxLayout(central)

            # Панель управления
            control_group = QGroupBox("Управление")
            control_layout = QVBoxLayout()

            # Выбор приложения
            app_layout = QHBoxLayout()
            self.app_combo = QComboBox()
            self.app_combo.addItems([
                "Выберите приложение...",
                "notepad.exe - Блокнот",
                "calc.exe - Калькулятор",
                "mspaint.exe - Paint",
                "write.exe - WordPad",
                "cmd.exe - Командная строка",
                "explorer.exe - Проводник",
                "Свой путь..."
            ])
            self.app_combo.currentIndexChanged.connect(self._on_app_selected)

            self.path_input = QLineEdit()
            self.path_input.setPlaceholderText("Или укажите полный путь к .exe...")

            browse_btn = QPushButton("Обзор...")
            browse_btn.clicked.connect(self._browse_exe)

            app_layout.addWidget(self.app_combo, 2)
            app_layout.addWidget(self.path_input, 3)
            app_layout.addWidget(browse_btn)
            control_layout.addLayout(app_layout)

            # Опции запуска
            options_layout = QHBoxLayout()
            self.wait_checkbox = QCheckBox("Ждать окно")
            self.wait_checkbox.setChecked(True)
            self.args_input = QLineEdit()
            self.args_input.setPlaceholderText("Аргументы (через пробел)...")

            options_layout.addWidget(self.wait_checkbox)
            options_layout.addWidget(self.args_input, 1)
            control_layout.addLayout(options_layout)

            # Кнопка запуска
            launch_btn = QPushButton("🚀 Запустить и зеркалировать")
            launch_btn.clicked.connect(self._launch_app)
            control_layout.addWidget(launch_btn)

            control_group.setLayout(control_layout)
            layout.addWidget(control_group)

            # MDI область
            self.mdi_area = QMdiArea()
            self.mdi_area.setViewMode(QMdiArea.TabbedView)
            self.mdi_area.setTabsClosable(True)
            self.mdi_area.setTabsMovable(True)
            layout.addWidget(self.mdi_area, 1)

            # Панель быстрого запуска
            quick_group = QGroupBox("Быстрый запуск")
            quick_layout = QHBoxLayout()

            apps = [
                ("📝", "Блокнот", "notepad.exe"),
                ("🧮", "Калькулятор", "calc.exe"),
                ("🎨", "Paint", "mspaint.exe"),
                ("📁", "Проводник", "explorer.exe ."),
                ("💻", "Командная строка", "cmd.exe"),
            ]

            for icon, name, cmd in apps:
                btn = QPushButton(f"{icon} {name}")
                btn.clicked.connect(lambda checked, c=cmd: self._quick_launch(c))
                quick_layout.addWidget(btn)

            quick_layout.addStretch()
            close_btn = QPushButton("❌ Закрыть все")
            close_btn.clicked.connect(self._close_all)
            quick_layout.addWidget(close_btn)

            quick_group.setLayout(quick_layout)
            layout.addWidget(quick_group)

            # Статус
            self.status_label = QLabel("Готов к работе")
            layout.addWidget(self.status_label)

            self.setCentralWidget(central)

        def _on_app_selected(self, index):
            """Обработка выбора приложения из списка."""
            if index == 0:  # "Выберите приложение..."
                return

            text = self.app_combo.currentText()

            # Парсим команду
            if " - " in text:
                cmd = text.split(" - ")[0]
            else:
                cmd = text

            if cmd == "Свой путь...":
                self.path_input.setFocus()
            else:
                self.path_input.setText(cmd)

        def _browse_exe(self):
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выберите исполняемый файл", "",
                "Executable files (*.exe);;All files (*.*)"
            )
            if file_path:
                self.path_input.setText(file_path)
                self.app_combo.setCurrentIndex(0)

        def _launch_app(self):
            exe_path = self.path_input.text().strip()
            if not exe_path:
                self.status_label.setText("❌ Укажите путь к приложению")
                return

            self.status_label.setText(f"⏳ Запуск {exe_path}...")

            args_text = self.args_input.text().strip()
            args = args_text.split() if args_text else []
            wait_for_window = self.wait_checkbox.isChecked()

            sub_window = self.mirror_manager.launch_and_mirror(
                self.mdi_area,
                exe_path,
                args,
                wait_for_window
            )

            if sub_window:
                self.status_label.setText(f"✅ {Path(exe_path).name} запущен")
            else:
                self.status_label.setText(f"❌ Не удалось запустить {exe_path}")

        def _quick_launch(self, cmd):
            """Быстрый запуск приложения."""
            self.path_input.setText(cmd)
            self._launch_app()

        def _close_all(self):
            """Закрыть все приложения."""
            self.mirror_manager.close_all()
            self.status_label.setText("Все приложения закрыты")

        def closeEvent(self, event):
            self.mirror_manager.close_all()
            event.accept()


    # Запуск тестового приложения
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    if sys.platform != "win32":
        print("❌ Это приложение работает только на Windows")
        sys.exit(1)

    try:
        import win32gui
    except ImportError:
        print("❌ Установите pywin32: pip install pywin32")
        sys.exit(1)

    window = ATestWindow()
    window.show()

    sys.exit(app.exec())
