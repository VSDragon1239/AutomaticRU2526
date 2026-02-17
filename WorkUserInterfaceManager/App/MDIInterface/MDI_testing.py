"""
Система зеркалирования окон с расширенным логированием для отладки.
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
    QApplication, QLabel, QSizePolicy, QFileDialog, QPushButton, QGroupBox, QHBoxLayout, QTextEdit, QMdiArea, QCheckBox,
    QLineEdit, QComboBox, QMainWindow
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QResizeEvent

import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32process
import win32api


# ============================================================================
# УТИЛИТЫ ДЛЯ ЛОГИРОВАНИЯ
# ============================================================================

def log_hex(value, name="value"):
    """Логирование в hex формате."""
    return f"{name}=0x{value:08X}"


def log_window_info(hwnd, prefix=""):
    """Логирование информации об окне."""
    try:
        title = win32gui.GetWindowText(hwnd)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        visible = win32gui.IsWindowVisible(hwnd)
        enabled = win32gui.IsWindowEnabled(hwnd)
        rect = win32gui.GetWindowRect(hwnd)

        info = [
            f"{prefix}hwnd={hwnd}",
            f"title='{title[:50]}{'...' if len(title) > 50 else ''}'",
            f"visible={visible}",
            f"enabled={enabled}",
            f"style={log_hex(style, 'style')}",
            f"ex_style={log_hex(ex_style, 'ex_style')}",
            f"rect={rect} ({rect[2] - rect[0]}x{rect[3] - rect[1]})"
        ]
        return " | ".join(info)
    except Exception as e:
        return f"{prefix}hwnd={hwnd} | Error: {e}"


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
# DWM THUMBNAIL MANAGER С ДЕТАЛЬНЫМ ЛОГИРОВАНИЕМ
# ============================================================================

class DWMThumbnailManager:
    """Менеджер для работы с DWM Thumbnails."""

    def __init__(self):
        self.dwmapi = ctypes.windll.dwmapi
        self._setup_prototypes()
        print(f"[DWM_Init] Библиотека dwmapi загружена: {self.dwmapi}")

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

        print("[DWM_Prototypes] Прототипы функций настроены")

    def register_thumbnail(self, dest_hwnd: int, source_hwnd: int) -> Optional[int]:
        """
        Регистрирует thumbnail для окна.

        Args:
            dest_hwnd: Handle окна-приемника
            source_hwnd: Handle окна-источника

        Returns:
            Thumbnail ID или None при ошибке
        """
        print(f"[DWM_Register] Начало регистрации thumbnail")
        print(f"[DWM_Register] dest_hwnd={dest_hwnd} ({log_hex(dest_hwnd)})")
        print(f"[DWM_Register] source_hwnd={source_hwnd} ({log_hex(source_hwnd)})")

        # Логируем информацию об окнах
        print(f"[DWM_Register] Окно назначения: {log_window_info(dest_hwnd, 'dest_')}")
        print(f"[DWM_Register] Окно источника: {log_window_info(source_hwnd, 'src_')}")

        thumbnail_id = ctypes.c_ulonglong()

        print("[DWM_Register] Вызов DwmRegisterThumbnail...")
        result = self.dwmapi.DwmRegisterThumbnail(
            ctypes.c_void_p(dest_hwnd),
            ctypes.c_void_p(source_hwnd),
            ctypes.byref(thumbnail_id)
        )

        print(f"[DWM_Register] DwmRegisterThumbnail вернул: {result} ({log_hex(result, 'result')})")
        print(f"[DWM_Register] thumbnail_id.value = {thumbnail_id.value}")

        if result == 0:  # S_OK
            print(f"[DWM_Register] Успешно! Thumbnail ID: {thumbnail_id.value}")
            return thumbnail_id.value
        else:
            print(f"[DWM_Register] Ошибка! Код: {result} ({log_hex(result)})")

            # Пробуем получить сообщение об ошибке
            error_codes = {
                0x80070057: "E_INVALIDARG - Неверные аргументы",
                0x8007000E: "E_OUTOFMEMORY - Недостаточно памяти",
                0x80070005: "E_ACCESSDENIED - Отказано в доступе",
                0x80070006: "E_HANDLE - Неверный handle",
            }

            if result in error_codes:
                print(f"[DWM_Register] Расшифровка: {error_codes[result]}")

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
        print(f"\n[DWM_Update] Начало обновления thumbnail")
        print(f"[DWM_Update] thumbnail_id={thumbnail_id}")
        print(f"[DWM_Update] rect={rect} ({rect[2] - rect[0]}x{rect[3] - rect[1]})")

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

            print(f"[DWM_Update] Свойства thumbnail:")
            print(f"  dwFlags={log_hex(props.dwFlags)}")
            print(f"  rcDestination=({props.rcDestination.left}, {props.rcDestination.top}, "
                  f"{props.rcDestination.right}, {props.rcDestination.bottom})")
            print(f"  rcSource=({props.rcSource.left}, {props.rcSource.top}, "
                  f"{props.rcSource.right}, {props.rcSource.bottom})")
            print(f"  fVisible={props.fVisible}")
            print(f"  fSourceClientAreaOnly={props.fSourceClientAreaOnly}")

            print("[DWM_Update] Вызов DwmUpdateThumbnailProperties...")
            result = self.dwmapi.DwmUpdateThumbnailProperties(
                ctypes.c_ulonglong(thumbnail_id),
                ctypes.byref(props)
            )

            print(f"[DWM_Update] DwmUpdateThumbnailProperties вернул: {result} ({log_hex(result, 'result')})")

            if result != 0:
                error_codes = {
                    0x80070057: "E_INVALIDARG - Неверные аргументы",
                    0x8007000E: "E_OUTOFMEMORY - Недостаточно памяти",
                    0x80070005: "E_ACCESSDENIED - Отказано в доступе",
                    0x80070006: "E_HANDLE - Неверный handle",
                    0x80004001: "E_NOTIMPL - Не реализовано",
                    0x80004002: "E_NOINTERFACE - Интерфейс не поддерживается",
                }

                if result in error_codes:
                    print(f"[DWM_Update] Расшифровка: {error_codes[result]}")

            success = result == 0
            print(f"[DWM_Update] Успех: {success}")
            return success

        except Exception as e:
            print(f"[DWM_Update] Исключение: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def unregister_thumbnail(self, thumbnail_id: int) -> bool:
        """
        Удаляет регистрацию thumbnail.

        Args:
            thumbnail_id: ID thumbnail

        Returns:
            True если успешно
        """
        print(f"[DWM_Unregister] Удаление thumbnail {thumbnail_id}")

        try:
            result = self.dwmapi.DwmUnregisterThumbnail(
                ctypes.c_ulonglong(thumbnail_id)
            )

            print(f"[DWM_Unregister] Результат: {result} ({log_hex(result)})")
            return result == 0
        except Exception as e:
            print(f"[DWM_Unregister] Ошибка: {e}")
            return False


# ============================================================================
# ВИДЖЕТ ДЛЯ ЗЕРКАЛИРОВАНИЯ ОКОН С ПОДРОБНЫМ ЛОГИРОВАНИЕМ
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
        self.is_mirroring = False
        self.update_timer = QTimer()
        self.last_screenshot = None
        self.screenshot_count = 0

        print(f"\n{'=' * 60}")
        print(f"[MirrorWidget] ИНИЦИАЛИЗАЦИЯ")
        print(f"[MirrorWidget] target_hwnd={target_hwnd} ({log_hex(target_hwnd)})")
        print(f"[MirrorWidget] parent={parent}")
        print(f"[MirrorWidget] self.winId()={self.winId()}")
        print(f"{'=' * 60}")

        self._setup_ui()
        self._setup_mirror()
        self._setup_update_timer()

    def _setup_ui(self) -> None:
        """Настройка базового UI."""
        print(f"[MirrorWidget_UI] Настройка интерфейса")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 150)

        # Фолбэк-лейбл
        self.fallback_label = QLabel("Инициализация зеркалирования...", self)
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.hide()

        # Стиль
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 2px solid #444;
            }
            QLabel {
                color: #ccc;
                font-family: Consolas, monospace;
                padding: 20px;
                font-size: 12px;
            }
        """)

        print(f"[MirrorWidget_UI] Виджет настроен, размер: {self.size()}")

    def _setup_mirror(self) -> None:
        """Настройка зеркалирования через DWM."""
        print(f"\n[MirrorWidget_Mirror] Настройка DWM зеркалирования")

        try:
            # Получаем handle Qt виджета
            qt_hwnd = int(self.winId())
            print(f"[MirrorWidget_Mirror] Qt widget hwnd: {qt_hwnd} ({log_hex(qt_hwnd)})")

            # Проверяем, что окно существует
            if not win32gui.IsWindow(self.target_hwnd):
                print(f"[MirrorWidget_Mirror] ОШИБКА: Окно {self.target_hwnd} не существует!")
                self._fallback_to_screenshot_mode()
                return

            print(f"[MirrorWidget_Mirror] Информация об окне-источнике:")
            print(f"  {log_window_info(self.target_hwnd)}")

            # Проверяем видимость окна
            if not win32gui.IsWindowVisible(self.target_hwnd):
                print(f"[MirrorWidget_Mirror] ПРЕДУПРЕЖДЕНИЕ: Окно не видимо!")

                # Пробуем показать окно
                try:
                    win32gui.ShowWindow(self.target_hwnd, win32con.SW_SHOW)
                    print(f"[MirrorWidget_Mirror] Окно показано")
                except:
                    print(f"[MirrorWidget_Mirror] Не удалось показать окно")

            # Пробуем активировать окно
            try:
                win32gui.SetForegroundWindow(self.target_hwnd)
                print(f"[MirrorWidget_Mirror] Окно активировано")
            except:
                print(f"[MirrorWidget_Mirror] Не удалось активировать окно")

            # Регистрируем thumbnail
            print(f"[MirrorWidget_Mirror] Регистрация DWM thumbnail...")
            self.thumbnail_id = self.dwm_manager.register_thumbnail(
                qt_hwnd,
                self.target_hwnd
            )

            if self.thumbnail_id:
                self.is_mirroring = True
                print(f"[MirrorWidget_Mirror] УСПЕХ: DWM thumbnail создан, ID: {self.thumbnail_id}")

                # Даем DWM время на инициализацию
                QTimer.singleShot(50, lambda: self._update_thumbnail_rect(first_time=True))

                # Пробуем обновить сразу
                self._update_thumbnail_rect(first_time=True)
            else:
                print(f"[MirrorWidget_Mirror] НЕУДАЧА: Не удалось создать DWM thumbnail")
                self._fallback_to_screenshot_mode()

        except Exception as e:
            print(f"[MirrorWidget_Mirror] ИСКЛЮЧЕНИЕ: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self._fallback_to_screenshot_mode()

    def _setup_update_timer(self) -> None:
        """Настройка таймера для обновления."""
        print(f"[MirrorWidget_Timer] Настройка таймера обновления")

        self.update_timer.timeout.connect(self._update_mirror)

        if self.is_mirroring:
            self.update_timer.start(100)  # 10 FPS для DWM
            print(f"[MirrorWidget_Timer] Таймер DWM: 100ms (10 FPS)")
        else:
            self.update_timer.start(500)  # 2 FPS для скриншотов
            print(f"[MirrorWidget_Timer] Таймер скриншотов: 500ms (2 FPS)")

    def _update_thumbnail_rect(self, first_time=False) -> None:
        """Обновление размера и позиции thumbnail."""
        if not self.is_mirroring or not self.thumbnail_id:
            return

        prefix = "[MirrorWidget_Thumbnail]" + (" [FIRST]" if first_time else "")

        try:
            rect = self.rect()
            print(f"{prefix} Обновление thumbnail")
            print(f"{prefix} Размер виджета: {rect.width()}x{rect.height()}")
            print(f"{prefix} rect object: {rect}")

            success = self.dwm_manager.update_thumbnail_properties(
                self.thumbnail_id,
                (0, 0, rect.width(), rect.height())
            )

            if success:
                print(f"{prefix} УСПЕХ: Thumbnail обновлен")

                # Принудительная перерисовка
                self.update()
                print(f"{prefix} Запрошена перерисовка виджета")

                # Проверяем видимость окна
                if not win32gui.IsWindowVisible(self.target_hwnd):
                    print(f"{prefix} ПРЕДУПРЕЖДЕНИЕ: Окно источника не видимо!")
            else:
                print(f"{prefix} НЕУДАЧА: Не удалось обновить thumbnail")

        except Exception as e:
            print(f"{prefix} ИСКЛЮЧЕНИЕ: {e}")

    def _fallback_to_screenshot_mode(self) -> None:
        """Фолбэк режим: периодические скриншоты окна."""
        print(f"\n[MirrorWidget_Fallback] Переключение в режим скриншотов")

        self.is_mirroring = False
        self.fallback_label.show()

        # Обновляем стиль для фолбэк режима
        self.setStyleSheet("""
            QWidget {
                background-color: #2a1e1e;
                border: 3px dashed #ff4444;
            }
            QLabel {
                color: #ff8888;
                font-family: Consolas, monospace;
                padding: 20px;
                font-size: 12px;
            }
        """)

        self.fallback_label.setText("РЕЖИМ СКРИНШОТОВ\n(DWM не доступен)\n\nОжидание окна...")
        print(f"[MirrorWidget_Fallback] Стиль и текст обновлены")

    def _capture_window_screenshot(self) -> Optional[QImage]:
        """Захватывает скриншот окна."""
        self.screenshot_count += 1
        call_id = self.screenshot_count

        print(f"\n[MirrorWidget_Screenshot#{call_id}] Захват скриншота")

        try:
            # Проверяем, существует ли окно
            if not win32gui.IsWindow(self.target_hwnd):
                print(f"[MirrorWidget_Screenshot#{call_id}] Окно не существует")
                return None

            # Получаем размеры и позицию окна
            rect = win32gui.GetWindowRect(self.target_hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            print(f"[MirrorWidget_Screenshot#{call_id}] Размеры окна: {width}x{height}")
            print(f"[MirrorWidget_Screenshot#{call_id}] Позиция: {rect}")

            if width <= 0 or height <= 0:
                print(f"[MirrorWidget_Screenshot#{call_id}] Неверные размеры окна")
                return None

            # Прямой захват через Windows API
            print(f"[MirrorWidget_Screenshot#{call_id}] Захват через GDI...")
            hdc_screen = win32gui.GetDC(0)
            hdc_mem = win32gui.CreateCompatibleDC(hdc_screen)
            hbitmap = win32gui.CreateCompatibleBitmap(hdc_screen, width, height)

            old_bitmap = win32gui.SelectObject(hdc_mem, hbitmap)

            # Копируем содержимое окна
            print(f"[MirrorWidget_Screenshot#{call_id}] BitBlt...")
            win32gui.BitBlt(
                hdc_mem, 0, 0, width, height,
                hdc_screen, rect[0], rect[1], win32con.SRCCOPY
            )

            # Восстанавливаем контекст
            win32gui.SelectObject(hdc_mem, old_bitmap)

            # Получаем информацию о bitmap
            bmpinfo = win32gui.GetObject(hbitmap)
            print(f"[MirrorWidget_Screenshot#{call_id}] Информация о bitmap: {bmpinfo}")

            bmpstr = win32gui.GetBitmapBits(hbitmap, True)
            print(f"[MirrorWidget_Screenshot#{call_id}] Получено байт: {len(bmpstr)}")

            # Создаем QImage
            print(f"[MirrorWidget_Screenshot#{call_id}] Создание QImage...")
            img = QImage(
                bmpstr,
                width,
                height,
                QImage.Format_ARGB32
            )

            print(f"[MirrorWidget_Screenshot#{call_id}] QImage создан:")
            print(f"  Размер: {img.width()}x{img.height()}")
            print(f"  Формат: {img.format()}")
            print(f"  Глубина цвета: {img.depth()} бит")
            print(f"  Bytes per line: {img.bytesPerLine()}")

            # Проверяем, не пустое ли изображение
            if img.isNull():
                print(f"[MirrorWidget_Screenshot#{call_id}] ОШИБКА: QImage пустой!")
            else:
                # Проверяем первые несколько пикселей
                if img.width() > 0 and img.height() > 0:
                    pixel = img.pixel(0, 0)
                    print(f"[MirrorWidget_Screenshot#{call_id}] Пиксель (0,0): {log_hex(pixel, 'pixel')}")

                # Конвертируем из BGR в RGB
                img = img.rgbSwapped()
                print(f"[MirrorWidget_Screenshot#{call_id}] Конвертирован BGR->RGB")

            # Очистка ресурсов GDI
            win32gui.DeleteObject(hbitmap)
            win32gui.DeleteDC(hdc_mem)
            win32gui.ReleaseDC(0, hdc_screen)

            print(f"[MirrorWidget_Screenshot#{call_id}] Ресурсы GDI освобождены")
            return img

        except Exception as e:
            print(f"[MirrorWidget_Screenshot#{call_id}] ИСКЛЮЧЕНИЕ: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _update_screenshot(self) -> None:
        """Обновление через скриншоты окна."""
        print(f"\n[MirrorWidget_UpdateScreenshot] Обновление скриншота")

        try:
            # Проверяем, существует ли еще окно
            if not win32gui.IsWindow(self.target_hwnd):
                print(f"[MirrorWidget_UpdateScreenshot] Окно закрыто")
                self.window_closed.emit(self.target_hwnd)
                self.fallback_label.setText("ОКНО ЗАКРЫТО")
                return

            print(f"[MirrorWidget_UpdateScreenshot] Информация об окне:")
            print(f"  {log_window_info(self.target_hwnd)}")

            # Захватываем скриншот
            img = self._capture_window_screenshot()

            if img is None or img.isNull():
                print(f"[MirrorWidget_UpdateScreenshot] Не удалось захватить скриншот")
                self.fallback_label.setText("НЕ УДАЛОСЬ ЗАХВАТИТЬ ОКНО")
                return

            # Сохраняем для возможного ресайза
            self.last_screenshot = img

            # Подготавливаем для отображения
            widget_size = self.size()
            print(f"[MirrorWidget_UpdateScreenshot] Размер виджета: {widget_size.width()}x{widget_size.height()}")

            scaled_img = img.scaled(
                widget_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            print(f"[MirrorWidget_UpdateScreenshot] Изображение масштабировано: "
                  f"{scaled_img.width()}x{scaled_img.height()}")

            pixmap = QPixmap.fromImage(scaled_img)
            print(f"[MirrorWidget_UpdateScreenshot] QPixmap создан: {pixmap.width()}x{pixmap.height()}")

            if pixmap.isNull():
                print(f"[MirrorWidget_UpdateScreenshot] ОШИБКА: QPixmap пустой!")
                self.fallback_label.setText("ОШИБКА: ПУСТОЙ PIXMAP")
            else:
                self.fallback_label.setPixmap(pixmap)
                self.fallback_label.setText("")  # Очищаем текст
                print(f"[MirrorWidget_UpdateScreenshot] Pixmap установлен в QLabel")

        except Exception as e:
            print(f"[MirrorWidget_UpdateScreenshot] ИСКЛЮЧЕНИЕ: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.fallback_label.setText(f"ОШИБКА: {str(e)[:50]}...")

    def _update_mirror(self) -> None:
        """Обновление зеркалирования."""
        # print(f"[MirrorWidget_Update] Обновление (is_mirroring={self.is_mirroring})")

        if not win32gui.IsWindow(self.target_hwnd):
            print(f"[MirrorWidget_Update] Окно закрыто, отправка сигнала")
            self.window_closed.emit(self.target_hwnd)
            return

        if self.is_mirroring:
            self._update_thumbnail_rect()
        else:
            self._update_screenshot()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Обработка изменения размера."""
        old_size = event.oldSize()
        new_size = event.size()

        print(f"\n[MirrorWidget_Resize] Изменение размера: {old_size.width()}x{old_size.height()} -> "
              f"{new_size.width()}x{new_size.height()}")

        super().resizeEvent(event)

        # Обновляем размер лейбла
        self.fallback_label.setGeometry(0, 0, self.width(), self.height())

        if self.is_mirroring:
            print(f"[MirrorWidget_Resize] Обновление thumbnail после ресайза")
            self._update_thumbnail_rect()
        elif self.last_screenshot is not None:
            print(f"[MirrorWidget_Resize] Обновление скриншота после ресайза")

            # Обновляем размер скриншота
            pixmap = QPixmap.fromImage(self.last_screenshot.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            self.fallback_label.setPixmap(pixmap)

    def paintEvent(self, event):
        """Переопределяем paintEvent для отладки."""
        super().paintEvent(event)

        # Для отладки: рисуем рамку
        if self.is_mirroring:
            from PySide6.QtGui import QPainter, QPen
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 3))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
            painter.drawText(10, 20, f"DWM: {self.thumbnail_id}")
            painter.drawText(10, 40, f"Size: {self.width()}x{self.height()}")

    def closeEvent(self, event) -> None:
        """Очистка ресурсов при закрытии."""
        print(f"\n[MirrorWidget_Close] Закрытие виджета")

        if self.thumbnail_id:
            print(f"[MirrorWidget_Close] Удаление thumbnail {self.thumbnail_id}")
            self.dwm_manager.unregister_thumbnail(self.thumbnail_id)
            self.thumbnail_id = None

        self.update_timer.stop()
        print(f"[MirrorWidget_Close] Таймер остановлен")

        event.accept()


# ============================================================================
# МЕНЕДЖЕР ЗЕРКАЛИРОВАНИЯ ПРИЛОЖЕНИЙ С ЛОГИРОВАНИЕМ
# ============================================================================

class AppMirrorManager:
    """Менеджер для запуска и зеркалирования приложений."""

    def __init__(self):
        self.mirrored_windows: Dict[int, Dict] = {}
        self.window_monitor_thread = None
        self.is_monitoring = False

        print(f"[AppMirrorManager] Инициализация менеджера")

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
        print(f"\n{'=' * 60}")
        print(f"[Launch] ЗАПУСК ПРИЛОЖЕНИЯ")
        print(f"[Launch] exe_path: {exe_path}")
        print(f"[Launch] args: {args}")
        print(f"[Launch] wait_for_window: {wait_for_window}")
        print(f"{'=' * 60}")

        try:
            # Проверяем существование файла
            if not Path(exe_path).exists():
                print(f"[Launch] Файл не существует: {exe_path}")

                # Пробуем найти стандартное приложение
                app_name = os.path.basename(exe_path)
                found_path = self._find_standard_app(app_name)
                if found_path:
                    exe_path = found_path
                    print(f"[Launch] Найден альтернативный путь: {exe_path}")
                else:
                    raise FileNotFoundError(f"Файл не найден: {exe_path}")
            else:
                print(f"[Launch] Файл существует: {exe_path}")

            # Запускаем процесс
            process_args = [exe_path]
            if args:
                process_args.extend(args)

            print(f"[Launch] Запуск процесса: {process_args}")

            # Используем CREATE_NO_WINDOW для консольных приложений
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            process = subprocess.Popen(
                process_args,
                creationflags=creation_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True  # Для запуска приложений из PATH
            )

            print(f"[Launch] Процесс запущен PID: {process.pid}")

            target_hwnd = None

            if wait_for_window:
                # Ждем создание главного окна
                print(f"[Launch] Ожидание окна (таймаут: 15 сек)...")
                target_hwnd = self._wait_for_main_window(process.pid, timeout=15)

                if not target_hwnd:
                    print(f"[Launch] Не удалось найти главное окно для PID {process.pid}")

                    # Пробуем найти любое окно процесса
                    print(f"[Launch] Поиск любого окна процесса...")
                    target_hwnd = self._find_any_process_window(process.pid)

                    if not target_hwnd:
                        print(f"[Launch] Окна не найдены, закрытие процесса")
                        process.terminate()
                        return None
            else:
                # Не ждем окно, создаем пустой виджет
                print(f"[Launch] Режим без ожидания окна")
                target_hwnd = 0

            if target_hwnd and target_hwnd != 0:
                print(f"[Launch] Найдено окно: hwnd={target_hwnd} ({log_hex(target_hwnd)})")
                print(f"[Launch] Информация об окне: {log_window_info(target_hwnd)}")

            # Создаем MDI окно
            print(f"[Launch] Создание MDI окна...")
            sub_window = QMdiSubWindow()

            if target_hwnd and target_hwnd != 0:
                title = self._get_window_title(target_hwnd)
                print(f"[Launch] Заголовок окна: '{title}'")
                sub_window.setWindowTitle(f"{title} (PID: {process.pid})")
            else:
                sub_window.setWindowTitle(f"{Path(exe_path).name} (PID: {process.pid})")

            sub_window.setAttribute(Qt.WA_DeleteOnClose)

            # Создаем виджет зеркалирования
            print(f"[Launch] Создание виджета зеркалирования...")
            if target_hwnd and target_hwnd != 0:
                mirror_widget = WindowMirrorWidget(target_hwnd)
            else:
                # Создаем заглушку
                print(f"[Launch] Создание заглушки (нет окна)")
                mirror_widget = QLabel(f"Приложение запущено\nPID: {process.pid}")
                mirror_widget.setAlignment(Qt.AlignCenter)
                mirror_widget.setStyleSheet("background-color: #333; color: #ccc; padding: 20px;")

            sub_window.setWidget(mirror_widget)

            # Настраиваем обработчики
            print(f"[Launch] Настройка обработчиков...")
            if hasattr(mirror_widget, 'window_closed'):
                mirror_widget.window_closed.connect(
                    lambda hwnd: self._on_mirrored_window_closed(hwnd, sub_window)
                )

            sub_window.destroyed.connect(
                lambda: self._on_mdi_window_closed(target_hwnd if target_hwnd else 0)
            )

            # Сохраняем информацию
            print(f"[Launch] Сохранение информации о зеркалируемом окне")
            self.mirrored_windows[target_hwnd if target_hwnd else 0] = {
                'process': process,
                'pid': process.pid,
                'sub_window': sub_window,
                'mirror_widget': mirror_widget,
                'exe_path': exe_path,
                'has_window': bool(target_hwnd and target_hwnd != 0)
            }

            # Добавляем в MDI область
            print(f"[Launch] Добавление в MDI область...")
            mdi_area.addSubWindow(sub_window)
            sub_window.show()

            print(f"[Launch] Размер MDI окна: {sub_window.size()}")

            # Запускаем мониторинг окон
            self._start_window_monitor()

            print(f"[Launch] УСПЕХ: Приложение зеркалировано")
            print(f"[Launch] Количество зеркалируемых окон: {len(self.mirrored_windows)}")

            return sub_window

        except Exception as e:
            print(f"[Launch] ОШИБКА: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", f"Не удалось запустить: {e}")
            return None

    def _find_standard_app(self, app_name: str) -> Optional[str]:
        """Поиск стандартных приложений Windows."""
        print(f"[FindApp] Поиск стандартного приложения: {app_name}")

        # Пути для поиска
        search_paths = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', app_name),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SysWOW64', app_name),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), app_name),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', app_name),
        ]

        # Для Windows 10/11 Calculator
        if app_name == "calc.exe":
            search_paths.extend([
                "C:\\Windows\\System32\\calc.exe",
                "C:\\Windows\\SysWOW64\\calc.exe",
                "C:\\Program Files\\WindowsApps\\Microsoft.WindowsCalculator*\\Calculator.exe"
            ])

        for path in search_paths:
            if os.path.exists(path):
                print(f"[FindApp] Найдено: {path}")
                return path

        print(f"[FindApp] Не найдено: {app_name}")
        return None

    def _wait_for_main_window(self, pid: int, timeout: int = 15) -> Optional[int]:
        """Ожидает создание главного окна процесса."""
        print(f"[WaitWindow] Ожидание окна для PID {pid} (таймаут: {timeout} сек)")

        start_time = time.time()
        last_check = 0

        while time.time() - start_time < timeout:
            hwnds = self._find_process_windows(pid)

            if hwnds:
                print(f"[WaitWindow] Найдено окон: {len(hwnds)}")

                for i, hwnd in enumerate(hwnds):
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        visible = win32gui.IsWindowVisible(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]

                        print(f"[WaitWindow] Окно {i + 1}: hwnd={hwnd}, "
                              f"title='{title}', visible={visible}, size={width}x{height}")

                        # Берем первое подходящее окно
                        if visible and title and width > 10 and height > 10:
                            print(f"[WaitWindow] Выбрано окно: {hwnd}")
                            return hwnd
                    except Exception as e:
                        print(f"[WaitWindow] Ошибка при проверке окна {hwnd}: {e}")

            # Логируем каждые 3 секунды
            if time.time() - last_check > 3:
                elapsed = time.time() - start_time
                print(f"[WaitWindow] Все еще ожидаю (прошло {elapsed:.1f} сек)...")
                last_check = time.time()

            time.sleep(0.5)

        print(f"[WaitWindow] Таймаут ожидания окна для PID {pid}")
        return None

    def _find_any_process_window(self, pid: int) -> Optional[int]:
        """Находит любое окно процесса без требований."""
        print(f"[FindAnyWindow] Поиск любого окна для PID {pid}")

        hwnds = self._find_process_windows(pid)

        if hwnds:
            print(f"[FindAnyWindow] Найдено окон: {len(hwnds)}")
            return hwnds[0]

        print(f"[FindAnyWindow] Окна не найдены")
        return None

    def _find_process_windows(self, pid: int) -> List[int]:
        """Находит все окна процесса."""
        print(f"[FindWindows] Поиск окон для PID {pid}")

        windows = []

        def enum_callback(hwnd, hwnds):
            if win32gui.IsWindow(hwnd):
                try:
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        hwnds.append(hwnd)
                except Exception as e:
                    print(f"[FindWindows] Ошибка получения PID для окна {hwnd}: {e}")
            return True

        try:
            win32gui.EnumWindows(enum_callback, windows)
        except Exception as e:
            print(f"[FindWindows] Ошибка перечисления окон: {e}")

        print(f"[FindWindows] Найдено окон: {len(windows)}")
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
            print("[Monitor] Мониторинг уже запущен")
            return

        print("[Monitor] Запуск мониторинга окон")
        self.is_monitoring = True
        self.window_monitor_thread = threading.Thread(
            target=self._window_monitor_loop,
            daemon=True
        )
        self.window_monitor_thread.start()
        print("[Monitor] Мониторинг окон запущен")

    def _window_monitor_loop(self) -> None:
        """Цикл мониторинга окон."""
        print("[Monitor_Loop] Начало цикла мониторинга")

        while self.is_monitoring and self.mirrored_windows:
            hwnds_to_remove = []

            for hwnd, info in self.mirrored_windows.items():
                # Для оконных приложений проверяем существование окна
                if info.get('has_window', False) and hwnd != 0:
                    if not win32gui.IsWindow(hwnd):
                        print(f"[Monitor_Loop] Окно {hwnd} закрыто")
                        hwnds_to_remove.append(hwnd)

                # Проверяем состояние процесса
                process = info['process']
                if process.poll() is not None:
                    print(f"[Monitor_Loop] Процесс {process.pid} завершен (код: {process.poll()})")
                    hwnds_to_remove.append(hwnd)

            # Удаляем закрытые окна/процессы
            for hwnd in hwnds_to_remove:
                if hwnd in self.mirrored_windows:
                    print(f"[Monitor_Loop] Закрытие MDI окна для hwnd {hwnd}")
                    QTimer.singleShot(0, lambda h=hwnd: self._close_mdi_for_window(h))

            time.sleep(1)

        print("[Monitor_Loop] Цикл мониторинга завершен")

    @Slot(int)
    def _on_mirrored_window_closed(self, hwnd: int, sub_window: QMdiSubWindow) -> None:
        """Обработка закрытия зеркалируемого окна."""
        print(f"[Event_WindowClosed] Зеркалируемое окно закрылось: {hwnd}")

        if hwnd in self.mirrored_windows:
            print(f"[Event_WindowClosed] Закрытие MDI окна")
            sub_window.close()

    @Slot()
    def _on_mdi_window_closed(self, hwnd: int) -> None:
        """Обработка закрытия MDI окна."""
        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]
            print(f"[Event_MdiClosed] Закрытие процесса для окна {hwnd} (PID: {info['pid']})")

            try:
                process = info['process']

                # Пытаемся закрыть корректно
                if process.poll() is None:
                    print(f"[Event_MdiClosed] Процесс еще работает, пытаемся закрыть...")

                    # Сначала WM_CLOSE для GUI окон
                    if hwnd != 0 and win32gui.IsWindow(hwnd):
                        try:
                            print(f"[Event_MdiClosed] Отправка WM_CLOSE окну {hwnd}")
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"[Event_MdiClosed] Ошибка WM_CLOSE: {e}")

                    # Terminate если еще жив
                    if process.poll() is None:
                        print(f"[Event_MdiClosed] Terminate процесса {info['pid']}")
                        process.terminate()

                        # Ждем завершения
                        try:
                            process.wait(timeout=1)
                            print(f"[Event_MdiClosed] Процесс завершен корректно")
                        except subprocess.TimeoutExpired:
                            print(f"[Event_MdiClosed] Таймаут, kill процесса")
                            process.kill()
                else:
                    print(f"[Event_MdiClosed] Процесс уже завершен")

            except Exception as e:
                print(f"[Event_MdiClosed] Ошибка при закрытии процесса: {e}")

            del self.mirrored_windows[hwnd]
            print(f"[Event_MdiClosed] Запись удалена из mirrored_windows")

    def _close_mdi_for_window(self, hwnd: int) -> None:
        """Закрывает MDI окно для указанного handle."""
        print(f"[CloseMdi] Закрытие MDI окна для hwnd {hwnd}")

        if hwnd in self.mirrored_windows:
            info = self.mirrored_windows[hwnd]
            info['sub_window'].close()
            print(f"[CloseMdi] MDI окно закрыто")
        else:
            print(f"[CloseMdi] hwnd {hwnd} не найден в mirrored_windows")

    def close_all(self) -> None:
        """Закрывает все зеркалируемые приложения."""
        print(f"\n[Manager_CloseAll] Закрытие всех приложений")
        print(f"[Manager_CloseAll] Количество приложений: {len(self.mirrored_windows)}")

        self.is_monitoring = False

        for hwnd, info in list(self.mirrored_windows.items()):
            print(f"[Manager_CloseAll] Закрытие hwnd={hwnd} (PID: {info['pid']})")
            self._on_mdi_window_closed(hwnd)

        print(f"[Manager_CloseAll] Все приложения закрыты")


# ============================================================================
# ТЕСТОВЫЙ ИНТЕРФЕЙС
# ============================================================================

class ATestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mirror_manager = AppMirrorManager()

        self._setup_ui()
        self.setWindowTitle("Window Mirroring Test - DEBUG")
        self.resize(1400, 800)

        # Консоль вывода
        import sys
        from io import StringIO

        class LogCapture(StringIO):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.stdout_backup = sys.stdout
                sys.stdout = self

            def write(self, text):
                self.text_widget.append(text.rstrip())
                self.stdout_backup.write(text)

            def flush(self):
                self.stdout_backup.flush()

        self.log_capture = LogCapture(self.log_text)

        print(f"{'=' * 60}")
        print(f"ТЕСТОВОЕ ПРИЛОЖЕНИЕ ЗАПУЩЕНО")
        print(f"Время: {time.strftime('%H:%M:%S')}")
        print(f"{'=' * 60}")

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
        self.path_input.setText("notepad.exe")  # По умолчанию

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

        # Кнопки
        buttons_layout = QHBoxLayout()
        launch_btn = QPushButton("🚀 Запустить и зеркалировать")
        launch_btn.clicked.connect(self._launch_app)

        test_dwm_btn = QPushButton("🔧 Тест DWM")
        test_dwm_btn.clicked.connect(self._test_dwm)

        buttons_layout.addWidget(launch_btn)
        buttons_layout.addWidget(test_dwm_btn)
        buttons_layout.addStretch()
        control_layout.addLayout(buttons_layout)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Основная область
        main_splitter = QHBoxLayout()

        # MDI область
        self.mdi_area = QMdiArea()
        self.mdi_area.setViewMode(QMdiArea.TabbedView)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)
        main_splitter.addWidget(self.mdi_area, 2)

        # Лог-консоль
        log_group = QGroupBox("Логи")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFontFamily("Consolas")
        self.log_text.setFontPointSize(9)
        self.log_text.setMaximumWidth(500)

        log_buttons = QHBoxLayout()
        clear_log_btn = QPushButton("Очистить логи")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())

        log_buttons.addWidget(clear_log_btn)
        log_buttons.addStretch()

        log_layout.addWidget(self.log_text)
        log_layout.addLayout(log_buttons)
        log_group.setLayout(log_layout)
        main_splitter.addWidget(log_group, 1)

        layout.addLayout(main_splitter, 1)

        # Панель быстрого запуска
        quick_group = QGroupBox("Быстрый запуск")
        quick_layout = QHBoxLayout()

        apps = [
            ("📝", "Блокнот", "notepad.exe"),
            ("🧮", "Калькулятор", "calc.exe"),
            ("🎨", "Paint", "mspaint.exe"),
            ("📁", "Проводник", "explorer.exe"),
            ("💻", "CMD", "cmd.exe"),
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
            print("[UI] ❌ Укажите путь к приложению")
            return

        print(f"\n{'=' * 60}")
        print(f"[UI] Запуск приложения: {exe_path}")
        print(f"{'=' * 60}")

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
            print(f"[UI] ✅ {Path(exe_path).name} запущен")
        else:
            print(f"[UI] ❌ Не удалось запустить {exe_path}")

    def _quick_launch(self, cmd):
        """Быстрый запуск приложения."""
        self.path_input.setText(cmd)
        self._launch_app()

    def _test_dwm(self):
        """Тест DWM функций."""
        print(f"\n{'=' * 60}")
        print(f"[UI] ТЕСТ DWM ФУНКЦИЙ")
        print(f"{'=' * 60}")

        # Простой тест: создаем окно и проверяем DWM
        import ctypes
        dwmapi = ctypes.windll.dwmapi

        # Проверяем, доступна ли DWM
        print(f"[DWM_Test] Проверка доступности DWM...")

        # Пробуем вызвать простую функцию
        try:
            is_composition_enabled = ctypes.c_int()
            result = dwmapi.DwmIsCompositionEnabled(ctypes.byref(is_composition_enabled))
            print(f"[DWM_Test] DwmIsCompositionEnabled: result={result}, enabled={is_composition_enabled.value}")
        except Exception as e:
            print(f"[DWM_Test] Ошибка DwmIsCompositionEnabled: {e}")

        # Проверяем версию DWM
        try:
            # Некоторые системные параметры
            from ctypes import wintypes

            class DWM_TIMING_INFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("rateRefresh", wintypes.UINT),
                    ("qpcRefreshPeriod", wintypes.UINT64),
                    ("rateCompose", wintypes.UINT),
                    ("qpcVBlank", wintypes.UINT64),
                    ("cRefresh", wintypes.UINT64),
                    ("qpcCompose", wintypes.UINT64),
                    ("cFrame", wintypes.UINT64),
                    ("cRefreshFrame", wintypes.UINT64),
                    ("cRefreshConfirmed", wintypes.UINT64),
                    ("cFlipsOutstanding", wintypes.UINT),
                ]

            timing_info = DWM_TIMING_INFO()
            timing_info.cbSize = ctypes.sizeof(DWM_TIMING_INFO)

            result = dwmapi.DwmGetCompositionTimingInfo(0, ctypes.byref(timing_info))
            print(f"[DWM_Test] DwmGetCompositionTimingInfo: result={result}")
        except Exception as e:
            print(f"[DWM_Test] Ошибка DwmGetCompositionTimingInfo: {e}")

    def _close_all(self):
        """Закрыть все приложения."""
        print(f"\n[UI] Закрытие всех приложений...")
        self.mirror_manager.close_all()
        print(f"[UI] Все приложения закрыты")

    def closeEvent(self, event):
        print(f"\n[UI] Закрытие приложения...")
        self.mirror_manager.close_all()

        # Восстанавливаем stdout
        import sys
        sys.stdout = self.log_capture.stdout_backup

        event.accept()
