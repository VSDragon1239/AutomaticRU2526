"""
Простое зеркалирование окна Obsidian.
"""

import sys
import subprocess
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32process
import win32ui
from PIL import ImageGrab
# from PyInstaller.compat import win32api

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QRect, QSize
from PySide6.QtGui import QImage, QPixmap


# ============================================================================
# ПРОСТОЙ МЕНЕДЖЕР ОКНА OBSIDIAN
# ============================================================================

class ObsidianWindowManager:
    """Менеджер для работы с окном Obsidian."""

    def __init__(self):
        self.obsidian_hwnd = None
        self.obsidian_pid = None
        self.obsidian_path = None

    def find_obsidian_window(self) -> bool:
        """Находит окно Obsidian."""
        print("[Obsidian] Поиск окна Obsidian...")

        def enum_callback(hwnd, found):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)

                # Ищем по заголовку
                if title and ("Obsidian" in title or "obsidian" in title.lower()):
                    print(f"[Obsidian] Найдено окно: hwnd={hwnd}, title='{title}'")
                    found.append(hwnd)
            return True

        found_windows = []
        win32gui.EnumWindows(enum_callback, found_windows)

        if found_windows:
            self.obsidian_hwnd = found_windows[0]

            # Получаем PID процесса
            _, pid = win32process.GetWindowThreadProcessId(self.obsidian_hwnd)
            self.obsidian_pid = pid

            print(f"[Obsidian] PID процесса: {pid}")
            return True

        print("[Obsidian] Окно Obsidian не найдено")
        return False

    def launch_obsidian(self, path: str = None) -> bool:
        """Запускает Obsidian."""
        print("[Obsidian] Запуск Obsidian...")

        # Пути для поиска Obsidian
        search_paths = [
            path,
            r"C:\Users\%USERNAME%\AppData\Local\Obsidian\Obsidian.exe",
            r"C:\Program Files\Obsidian\Obsidian.exe",
            r"C:\Program Files (x86)\Obsidian\Obsidian.exe",
        ]

        exe_path = None
        for p in search_paths:
            if p and isinstance(p, str):
                import os
                expanded_path = os.path.expandvars(p)
                if os.path.exists(expanded_path):
                    exe_path = expanded_path
                    break

        if not exe_path:
            print("[Obsidian] Obsidian не найден")
            return False

        print(f"[Obsidian] Запуск: {exe_path}")

        try:
            process = subprocess.Popen([exe_path])
            self.obsidian_pid = process.pid
            self.obsidian_path = exe_path

            print(f"[Obsidian] Запущен, PID: {process.pid}")

            # Ждем создание окна
            for _ in range(30):  # 30 попыток по 0.5 сек = 15 секунд
                if self.find_obsidian_window():
                    return True
                time.sleep(0.5)

            print("[Obsidian] Не удалось найти окно после запуска")
            return False

        except Exception as e:
            print(f"[Obsidian] Ошибка запуска: {e}")
            return False


# ============================================================================
# ПРОСТОЙ ВИДЖЕТ ДЛЯ ЗЕРКАЛИРОВАНИЯ
# ============================================================================

class SimpleMirrorWidget(QWidget):
    """Простой виджет для зеркалирования окна."""

    def __init__(self, target_hwnd: int):
        super().__init__()
        self.target_hwnd = target_hwnd
        self.update_timer = QTimer()

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Настройка интерфейса."""
        self.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")

        self.image_label = QLabel("Инициализация...", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: #ccc; font-size: 14px; padding: 20px;")
        self.setMaximumSize(QSize(800, 800))

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

    def setup_timer(self):
        """Настройка таймера."""
        self.update_timer.timeout.connect(self.update_mirror)
        self.update_timer.start(100)  # 10 FPS

    def capture_screenshot(self) -> QImage:
        """Захватывает скриншот окна."""
        try:
            if not win32gui.IsWindow(self.target_hwnd):
                return None

            # Получаем размеры окна
            rect = win32gui.GetWindowRect(self.target_hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                return None

            # Получаем DC окна
            hwnd_dc = win32gui.GetWindowDC(self.target_hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # Создаем битмап
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)

            # Пробуем PrintWindow (лучше работает с аппаратным ускорением)
            try:
                result = ctypes.windll.user32.PrintWindow(
                    self.target_hwnd,
                    save_dc.GetSafeHdc(),
                    2  # PW_RENDERFULLCONTENT - захватывает все содержимое
                )

                if result == 0:
                    print("[Mirror] PrintWindow failed, falling back to BitBlt")
                    # Если PrintWindow не сработал, пробуем BitBlt
                    save_dc.BitBlt(
                        (0, 0),
                        (width, height),
                        mfc_dc,
                        (0, 0),
                        win32con.SRCCOPY
                    )
            except Exception as e:
                print(f"[Mirror] PrintWindow error: {e}")
                save_dc.BitBlt(
                    (0, 0),
                    (width, height),
                    mfc_dc,
                    (0, 0),
                    win32con.SRCCOPY
                )

            # Получаем информацию о битмапе
            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)

            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: правильный расчет stride
            # QImage ожидает данные с выравниванием по 32 бита
            stride = ((width * 32 + 31) // 32) * 4

            # Создаем QImage с правильными параметрами
            # Используем Format_ARGB32 для прозрачности
            img = QImage(
                bmpstr,
                width,
                height,
                stride,
                QImage.Format_ARGB32
            )

            # Создаем копию, чтобы данные не освобождались раньше времени
            img_copy = img.copy()

            # Очистка ресурсов В ПРАВИЛЬНОМ ПОРЯДКЕ
            # Важно: сначала отвязываем bitmap от DC, потом удаляем
            # save_dc.SelectObject(win32ui.CreateBitmap())

            # Удаляем объекты
            # bitmap.DeleteObject()
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.target_hwnd, hwnd_dc)

            return img_copy

        except Exception as e:
            print(f"[Mirror] Ошибка захвата: {e}")
            import traceback
            traceback.print_exc()
            return None

    def capture_screenshot_pil(self) -> QImage:
        """Захватывает скриншот окна через PIL."""
        try:
            if not win32gui.IsWindow(self.target_hwnd):
                return None

            # Получаем размеры окна
            rect = win32gui.GetWindowRect(self.target_hwnd)

            # Приводим окно на передний план для захвата
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.05)  # Ждем обновления

            # Захватываем область экрана
            screenshot = ImageGrab.grab(bbox=rect)

            # Конвертируем PIL Image в QImage
            screenshot = screenshot.convert("RGBA")
            data = screenshot.tobytes("raw", "RGBA")
            img = QImage(data, screenshot.width, screenshot.height, QImage.Format_RGBA8888)

            return img.copy()

        except Exception as e:
            print(f"[Mirror] Ошибка захвата через PIL: {e}")
            return None

    def update_mirror(self):
        """Обновление зеркала."""
        if not win32gui.IsWindow(self.target_hwnd):
            self.image_label.setText("Окно Obsidian закрыто")
            self.update_timer.stop()  # Останавливаем таймер
            return

        img = self.capture_screenshot()

        if img and not img.isNull():
            # Сохраняем ссылку на старый pixmap для очистки
            old_pixmap = self.image_label.pixmap()

            # Масштабируем под размер виджета
            scaled_img = img.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            pixmap = QPixmap.fromImage(scaled_img)
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")

            # Явно очищаем старый pixmap
            if old_pixmap:
                del old_pixmap
        else:
            self.image_label.setText("Не удалось захватить окно")

    def resizeEvent(self, event):
        """Обработка изменения размера."""
        super().resizeEvent(event)
        self.image_label.setGeometry(0, 0, self.width(), self.height())


# ============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# ============================================================================

class ObsidianMirrorApp(QMainWindow):
    """Главное окно приложения для зеркалирования Obsidian."""

    def __init__(self):
        super().__init__()
        self.window_manager = ObsidianWindowManager()
        self.mirror_widget = None

        self.setup_ui()
        self.try_find_obsidian()

    def setup_ui(self):
        """Настройка интерфейса."""
        self.setWindowTitle("Obsidian Mirror")
        self.setGeometry(100, 100, 800, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель управления
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet("color: #ccc; font-size: 12px; padding: 5px;")

        self.refresh_btn = QPushButton("🔍 Найти Obsidian")
        self.refresh_btn.clicked.connect(self.try_find_obsidian)

        self.launch_btn = QPushButton("🚀 Запустить Obsidian")
        self.launch_btn.clicked.connect(self.launch_obsidian)

        control_layout.addWidget(self.status_label, 1)
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.launch_btn)

        layout.addWidget(control_panel)

        # Область для зеркала
        self.mirror_container = QWidget()
        self.mirror_container.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        layout.addWidget(self.mirror_container, 1)

        # Информация
        info_label = QLabel(
            "Простое зеркалирование окна Obsidian. "
            "Если Obsidian уже запущен, он будет найден автоматически."
        )
        info_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def try_find_obsidian(self):
        """Попытка найти и подключиться к Obsidian."""
        self.status_label.setText("Поиск Obsidian...")

        if self.window_manager.find_obsidian_window():
            self.setup_mirror()
            self.status_label.setText(
                f"✓ Подключено к Obsidian (PID: {self.window_manager.obsidian_pid})"
            )
        else:
            self.status_label.setText("✗ Obsidian не найден")

    def launch_obsidian(self):
        """Запуск Obsidian."""
        self.status_label.setText("Запуск Obsidian...")

        if self.window_manager.launch_obsidian():
            self.setup_mirror()
            self.status_label.setText(
                f"✓ Obsidian запущен (PID: {self.window_manager.obsidian_pid})"
            )
        else:
            QMessageBox.warning(
                self,
                "Obsidian не найден",
                "Не удалось найти или запустить Obsidian.\n\n"
                "Укажите путь к Obsidian.exe вручную."
            )
            self.status_label.setText("✗ Не удалось запустить Obsidian")

    def setup_mirror(self):
        """Настройка зеркала."""
        if not self.window_manager.obsidian_hwnd:
            return

        # Удаляем старый виджет
        if self.mirror_widget:
            self.mirror_widget.deleteLater()

        # Создаем новый
        self.mirror_widget = SimpleMirrorWidget(self.window_manager.obsidian_hwnd)

        # Очищаем контейнер и добавляем виджет
        layout = QVBoxLayout(self.mirror_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mirror_widget)

        print(f"[App] Зеркало настроено для окна: {self.window_manager.obsidian_hwnd}")


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

# def main():
#     """Главная функция."""
#     app = QApplication(sys.argv)
#     app.setStyle('Fusion')
#
#     # Проверка платформы
#     if sys.platform != "win32":
#         print("Это приложение работает только на Windows")
#         return 1
#
#     # Проверка зависимостей
#     try:
#         import win32gui
#     except ImportError:
#         print("Установите pywin32: pip install pywin32")
#         return 1
#
#     # Запуск приложения
#     window = ObsidianMirrorApp()
#     window.show()
#
#     return app.exec()
#
#
# if __name__ == "__main__":
#     sys.exit(main())
