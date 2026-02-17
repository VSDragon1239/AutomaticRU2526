from PySide6.QtGui import QFontDatabase

from WorkUserInterfaceManager.App.Tools.LoggingCustom import get_logger_img
from WorkUserInterfaceManager.settings import main_font_path, main_font_name


def set_style_sheet(widget, logger):
    styleSheet = f"""
QLabel {{
    border-radius: 3px;
    padding: 3px;
}}

QWidget {{
    border: 1px solid rgb(0, 100, 100);
    color: rgb(100, 200, 200);
    background-color: rgba(20, 30, 40, 100);
    border-radius: 3px;
    padding: 3px;
    font-family: {main_font_name[:-4]};
    font-weight: bold;
    font-size: 18px;
}}

/* ==================  Кнопки  ================== */

QPushButton {{  
    background-color: rgb(10, 80, 100);
    color: rgb(100, 200, 200);
    border-radius: 5px;
}}  
  
QPushButton:hover {{  
    background-color: rgb(20, 100, 120);
}}  
  
QPushButton:pressed {{  
    background-color: rgb(0, 60, 80);
}}

/* ==================  Главная / Документация  ================== */

QTabWidget::pane {{
    border: 1px solid rgb(0, 100, 100);
    background-color: rgba(0, 30, 40, 180);
}}

QTabBar {{
    background: rgba(0, 10, 80, 100);
    border-bottom: 1px solid rgb(0, 100, 100);
}}

QTabBar::tab {{
    color: rgb(100, 200, 200);
    padding: 6px 12px;
    border: 1px solid rgb(0, 100, 100);
    border-bottom: none;
    min-width: 80px;
}}

QTabBar::tab:selected {{
    color: rgb(180, 255, 255);
    background: rgb(0, 60, 80);
}}

QTabBar::tab:hover {{
    background: rgb(0, 60, 80);
}}

QTabBar::tab:!selected {{
    margin-top: 3px;
}}
"""


    logger.info(f"{get_logger_img('Инициализация')} - MainInterface[↴] - set_style_sheet - Установка addApplicationFont(main_font_path) интерфейсу...")
    QFontDatabase.addApplicationFont(main_font_path.replace('\\', '/'))

    logger.info(f"{get_logger_img('Инициализация')} - MainInterface[↴] - set_style_sheet - Установка setStyleSheet интерфейсу...")
    widget.setStyleSheet(styleSheet)
