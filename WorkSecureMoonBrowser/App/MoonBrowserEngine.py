import sys
import os
import shutil
import ssl
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QToolBar, QStatusBar,
                               QWidget, QTabWidget, QProgressBar, QMessageBox,
                               QDialog, QLabel, QDialogButtonBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (QWebEngineSettings, QWebEngineProfile,
                                     QWebEnginePage, QWebEngineUrlRequestInterceptor)
from PySide6.QtCore import QUrl, Qt, QSize, QByteArray
from PySide6.QtGui import QFont

# ==========================================
# НАСТРОЙКИ БЕЗОПАСНОСТИ И СТАРТА
# ==========================================

# Вкладки, которые откроются сразу при запуске
STARTUP_URLS = [
    "https://www.google.com",
    "https://mail.ru",
    # "https://vk.com", # Раскомментируйте нужные
]

# Имя папки для хранения данных (создается рядом с .py файлом)
# В этой папке лежат куки, кэш и история. Удалив её — вы удалите все следы.
DATA_DIR_NAME = "Moon_Data_Vault"

STYLESHEET = """
/* === ГЛОБАЛЬНЫЕ НАСТРОЙКИ === */
QMainWindow, QWidget {
    background-color: #202124;
    color: #e8eaed;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
}

/* === ВКЛАДКИ (TABS) === */
QTabWidget::pane {
    border: none;
    background-color: #202124;
}

QTabBar {
    background: #202124;
    qproperty-drawBase: 0;
    border-bottom: 1px solid #3c4043;
}

QTabBar::tab {
    background: #202124; /* Неактивная вкладка сливается с фоном */
    color: #9aa0a6;
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 100px;
}

QTabBar::tab:selected {
    background: #202124; /* Фон вкладки */
    color: #e8eaed;
    border-bottom: 2px solid #8e44ad; /* Акцентная линия снизу */
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: #292a2d;
}

/* Кнопка закрытия вкладки */
QTabBar::close-button {
    image: none;
    subcontrol-position: right;
    margin-right: 4px;
}
QTabBar::close-button:hover {
    background-color: #e74c3c;
    border-radius: 4px;
}

/* === ПАНЕЛЬ ИНСТРУМЕНТОВ (TOOLBAR) === */
QToolBar {
    background: #202124;
    border: none;
    spacing: 8px;
    padding: 6px 12px;
    border-bottom: 1px solid #3c4043;
}

/* Кнопки навигации */
QPushButton {
    background: transparent;
    color: #9aa0a6;
    border: none;
    border-radius: 50%; /* Круглые кнопки */
    padding: 8px;
    width: 32px;
    height: 32px;
    font-size: 16px;
}

QPushButton:hover {
    background: #3c4043;
    color: #ffffff;
}

QPushButton:pressed {
    background: #5f6368;
}

/* === ПОЛЕ АДРЕСА (OMNIBOX) === */
QLineEdit#url_bar {
    background: #35363a;
    color: #e8eaed;
    border: 2px solid transparent;
    border-radius: 24px; /* Сильное скругление как в Chrome */
    padding: 6px 16px;
    font-size: 14px;
    selection-background-color: #8e44ad;
}

QLineEdit#url_bar:focus {
    background: #202124;
    border: 2px solid #8e44ad; /* Акцент при фокусе */
}

/* Кнопки внутри панели (Пойти, Безопасность) */
QPushButton#action_btn {
    background: #8e44ad;
    color: white;
    border-radius: 16px;
    padding: 6px 16px;
    width: auto;
    height: auto;
    font-weight: bold;
}
QPushButton#action_btn:hover {
    background: #9b59b6;
}

/* === СТАТУС БАР === */
QStatusBar {
    background: #171717;
    color: #9aa0a6;
    border-top: 1px solid #3c4043;
    font-size: 12px;
    padding: 4px;
}

/* === ПРОГРЕСС БАР === */
QProgressBar {
    background-color: #3c4043;
    border: none;
    height: 3px;
    border-radius: 1.5px;
    text-align: center;
    color: transparent; /* Скрываем текст % */
}
QProgressBar::chunk {
    background-color: #8e44ad;
    border-radius: 1.5px;
}

/* === ДИАЛОГИ И СООБЩЕНИЯ === */
QMessageBox, QDialog {
    background-color: #202124;
}
QLabel {
    color: #e8eaed;
}
QPushButton {
    min-width: 80px;
}
"""


class PrivacyRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Перехватчик сетевых запросов для повышения приватности.
    Удаляет Referer и добавляет DNT.
    """

    def interceptRequest(self, info):
        # Отключаем Referer, чтобы сайты не знали, откуда мы пришли
        info.setHttpHeader(b"Referer", b"")
        # Отправляем сигнал "Do Not Track"
        info.setHttpHeader(b"DNT", b"1")


class SSLCertificateDialog(QDialog):
    """Диалоговое окно предупреждения о проблемах SSL"""

    def __init__(self, error_description, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️ Критическая ошибка безопасности")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui(error_description, url)
        self.setStyleSheet(STYLESHEET)  # Применяем тему к диалогу

    def setup_ui(self, error_description, url):
        layout = QVBoxLayout(self)

        warning_label = QLabel("🛑 ВНИМАНИЕ 🛑")
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(warning_label)

        text_label = QLabel(
            f"<h3>Небезопасное соединение</h3>"
            f"<p>Сайт: <b>{url}</b></p>"
            f"<p>Ошибка сертификата: <i>{error_description}</i></p>"
            f"<p>Возможно, соединение перехватывается злоумышленниками.</p>"
            f"<p><b>Настоятельно рекомендуется закрыть эту страницу.</b></p>"
        )
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        button_box = QDialogButtonBox()
        self.continue_btn = button_box.addButton("Продолжить (Опасно)", QDialogButtonBox.AcceptRole)
        self.cancel_btn = button_box.addButton("Закрыть вкладку", QDialogButtonBox.RejectRole)

        self.continue_btn.setStyleSheet("background-color: #c0392b; color: white; padding: 5px;")
        self.cancel_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 5px;")

        layout.addWidget(button_box)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)


class SecureWebEnginePage(QWebEnginePage):
    """Кастомная страница с обработкой ошибок SSL"""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.ssl_errors_ignored = set()

    def certificateError(self, certificateError):
        url = certificateError.url().toString()
        error_description = certificateError.description()

        # Автоматический пропуск для localhost (если нужно для разработки)
        if 'localhost' in url or '127.0.0.1' in url:
            certificateError.ignoreCertificateError()
            return True

        # Если пользователь уже подтвердил риск для этого URL
        if url in self.ssl_errors_ignored:
            certificateError.ignoreCertificateError()
            return True

        # Показываем диалог
        dialog = SSLCertificateDialog(error_description, url, self.parent())
        if dialog.exec() == QDialog.Accepted:
            self.ssl_errors_ignored.add(url)
            certificateError.ignoreCertificateError()
            return True

        return False


class MoonBrowser(QMainWindow):
    def __init__(self, data_path):
        super().__init__()
        self.data_path = data_path
        self.setWindowTitle("Luna's Secure Moon Browser 🌙 [Private Mode]")
        self.setGeometry(100, 100, 1200, 800)

        # Настройка темы
        # self.setup_moon_theme()
        self.setStyleSheet(STYLESHEET)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создание вкладок
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # Панель навигации
        self.create_navigation_bar()
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.tabs)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.ssl_status = QPushButton("🔒")
        self.ssl_status.setEnabled(False)
        self.ssl_status.setFlat(True)
        self.status_bar.addPermanentWidget(self.ssl_status)

        # Инициализация безопасного профиля
        self.secure_profile = self.create_secure_profile()

        # Открытие стартовых вкладок
        if STARTUP_URLS:
            for url in STARTUP_URLS:
                self.add_new_tab(QUrl(url))
        else:
            self.add_new_tab(QUrl("https://www.google.com"), "Новая вкладка")

    def create_secure_profile(self):
        """
        Создает изолированный профиль браузера.
        Все данные сохраняются ТОЛЬКО в указанной папке.
        """
        profile = QWebEngineProfile("MoonSecureProfile", self)

        # Устанавливаем пути кэша и данных в локальную папку
        # Это ключевой момент для переносимости (portability)
        profile.setPersistentStoragePath(os.path.join(self.data_path, "Storage"))
        profile.setCachePath(os.path.join(self.data_path, "Cache"))

        # Настройки куки: разрешаем персистентность, но только в нашей папке
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)

        # HTTP кэш в памяти для скорости, но персистентный для оффлайна (опционально)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)

        # Подключаем перехватчик запросов для приватности
        interceptor = PrivacyRequestInterceptor(profile)
        profile.setUrlRequestInterceptor(interceptor)

        # Настройки безопасности по умолчанию для профиля
        settings = profile.settings()
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        # settings.setAttribute(QWebEngineSettings.AllowGeolocationInsecureOrigins, False)
        # Отключаем плагины (Flash устарел, но на всякий случай)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)

        return profile

    def setup_moon_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #1a1a2e; }
            QTabWidget::pane { border: 2px solid #8e44ad; background-color: #16213e; }
            QTabBar::tab {
                background: #16213e; color: #ecf0f1;
                padding: 8px 20px; margin-right: 2px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #8e44ad; color: white; font-weight: bold; }
            QTabBar::tab:hover { background: #1e3a5f; }
            QLineEdit {
                background: #0f3460; color: white; border: 1px solid #8e44ad;
                border-radius: 10px; padding: 6px 10px; font-size: 13px;
            }
            QPushButton {
                background: #8e44ad; color: white; border-radius: 8px;
                padding: 5px 10px; font-weight: bold;
            }
            QPushButton:hover { background: #9b59b6; }
            QPushButton:pressed { background: #7d3c98; }
            QStatusBar { background: #0f3460; color: #bdc3c7; }
        """)

    def create_navigation_bar(self):
        self.nav_bar = QToolBar()
        self.nav_bar.setMovable(False)
        self.nav_bar.setIconSize(QSize(24, 24))

        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(35, 35)
        self.back_btn.clicked.connect(self.navigate_back)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(35, 35)
        self.forward_btn.clicked.connect(self.navigate_forward)

        self.reload_btn = QPushButton("⟳")
        self.reload_btn.setFixedSize(35, 35)
        self.reload_btn.clicked.connect(self.navigate_reload)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("🔒 Введите безопасный адрес...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.go_btn = QPushButton("Перейти")
        self.go_btn.clicked.connect(self.navigate_to_url)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setToolTip("Новая вкладка")
        self.new_tab_btn.setFixedSize(35, 35)
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())

        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.setToolTip("Уничтожить все данные сессии")
        self.clear_btn.setFixedSize(35, 35)
        self.clear_btn.setStyleSheet("background-color: #c0392b;")
        self.clear_btn.clicked.connect(self.clear_all_data)

        self.nav_bar.addWidget(self.back_btn)
        self.nav_bar.addWidget(self.forward_btn)
        self.nav_bar.addWidget(self.reload_btn)
        self.nav_bar.addWidget(self.url_bar)
        self.nav_bar.addWidget(self.go_btn)
        self.nav_bar.addWidget(self.new_tab_btn)
        self.nav_bar.addWidget(self.clear_btn)

    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        # Используем нашу кастомную страницу с безопасным профилем
        page = SecureWebEnginePage(self.secure_profile, browser)
        browser.setPage(page)

        browser.setUrl(qurl)

        # Подключение сигналов
        browser.urlChanged.connect(self.update_urlbar)
        browser.loadStarted.connect(self.webview_load_started)
        browser.loadProgress.connect(self.webview_load_progress)
        browser.loadFinished.connect(self.webview_load_finished)
        browser.titleChanged.connect(lambda title: self.update_tab_title(browser, title))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return browser

    def close_tab(self, i):
        if self.tabs.count() < 2:
            self.close()  # Закрываем браузер, если это последняя вкладка
            return

        browser = self.tabs.widget(i)
        if browser:
            # Остановка загрузки и удаление
            browser.stop()
            browser.page().deleteLater()
            browser.deleteLater()

        self.tabs.removeTab(i)

    def update_urlbar(self, q):
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

        # Визуальная индикация безопасности
        if q.scheme() == 'https':
            self.ssl_status.setText("🔒 SSL")
            self.ssl_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.url_bar.setStyleSheet(
                "background: #0f3460; border: 2px solid #2ecc71; border-radius: 10px; padding: 6px;")
        else:
            self.ssl_status.setText("⚠️ HTTP")
            self.ssl_status.setStyleSheet("color: #e67e22; font-weight: bold;")
            self.url_bar.setStyleSheet(
                "background: #2c3e50; border: 2px solid #e67e22; border-radius: 10px; padding: 6px;")

    def update_tab_title(self, browser, title):
        i = self.tabs.indexOf(browser)
        if i != -1:
            lock = "🔒 " if browser.url().scheme() == 'https' else "⚠️ "
            self.tabs.setTabText(i, lock + (title[:20] + "..." if len(title) > 20 else title))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return

        # Автоматическая подстановка https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    # Стандартные методы навигации
    def navigate_back(self):
        if self.tabs.currentWidget(): self.tabs.currentWidget().back()

    def navigate_forward(self):
        if self.tabs.currentWidget(): self.tabs.currentWidget().forward()

    def navigate_reload(self):
        if self.tabs.currentWidget(): self.tabs.currentWidget().reload()

    # Индикаторы загрузки
    def webview_load_started(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Загрузка...")

    def webview_load_progress(self, p):
        self.progress_bar.setValue(p)

    def webview_load_finished(self, success):
        self.progress_bar.setVisible(False)
        msg = "Готово" if success else "Ошибка загрузки"
        self.status_bar.showMessage(msg, 3000)

    def current_tab_changed(self, i):
        if i >= 0:
            browser = self.tabs.widget(i)
            if browser:
                self.update_urlbar(browser.url())

    def clear_all_data(self):
        """Принудительная очистка всех данных профиля"""
        reply = QMessageBox.question(self, 'Уничтожение данных',
                                     "Вы уверены, что хотите очистить кэш, куки и историю?\n"
                                     "Это действие удалит все данные сессии.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Очистка через API профиля
            self.secure_profile.clearAllVisitedLinks()
            self.secure_profile.clearHttpCache()

            # Показываем сообщение
            QMessageBox.information(self, "Успешно", "Данные очищены из памяти.")
            # Перезагружаем вкладки для применения чистого состояния
            for i in range(self.tabs.count()):
                self.tabs.widget(i).reload()

    def closeEvent(self, event):
        """Обработчик закрытия окна с вопросом об удалении файлов"""
        reply = QMessageBox.question(self, 'Выход',
                                     "Завершить работу браузера?\n\n"
                                     "<b>Удалить папку с данными профиля?</b>\n"
                                     f"(Папка: {self.data_path})\n\n"
                                     "Выберите действие для безопасности:",
                                     QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            event.ignore()
        else:
            # Сохраняем геометрию или другие настройки, если нужно
            if reply == QMessageBox.Discard:
                try:
                    # Полное удаление папки данных с диска
                    if os.path.exists(self.data_path):
                        shutil.rmtree(self.data_path)
                        print(f"Папка данных {self.data_path} успешно удалена.")
                except Exception as e:
                    print(f"Ошибка при удалении данных: {e}")
            event.accept()


def main():
    # Определяем путь к данным рядом с исполняемым файлом/скриптом
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, DATA_DIR_NAME)

    # Создаем папку, если её нет (Qt иногда капризничает)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Настройка переменных окружения для Chromium
    # Отключаем GPU для предотвращения некоторых атак через драйверы (опционально)
    # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

    app = QApplication(sys.argv)
    app.setApplicationName("MoonBrowserSecure")

    # Установка шрифта
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MoonBrowser(data_path)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
