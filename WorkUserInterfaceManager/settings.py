import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = str(Path(sys.executable).resolve().parent).replace('\\', '/') + "/bin"
else:
    # BASE_DIR = Path(__file__).resolve().parent
    BASE_DIR = str(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/') + '/TestApp/v0/'

UI_DIR = str(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/') + '/App/XMLFiles/'

UI_FILES = [
    "main_window",
    "new_main_window",
]

PY_UI_FILES = [
    "main_window",
    "new_main_window",
]

RESOURCES_DIR = str(BASE_DIR).replace("\\", "/") + 'resources/'

SYSTEM_IMAGES_DIR = RESOURCES_DIR + 'sysimg/'
USER_IMAGES_DIR = RESOURCES_DIR + 'img/'

APP_ICONS_DIR = RESOURCES_DIR + 'AppDataIcons/'

FONTS_DIR = RESOURCES_DIR + 'fonts/'

USER_IMAGE_FILES = [
    "user.png",
]

SYSTEM_IMAGE_FILES = [
    "icon.png",
    "button.png",
    "button_active.png",
    "button_hover.png",
    "background.png",
    "background.gif",
    "base_project_1.png",
    "base_project_2.png",
    "base_project_3.png",
    "base_project_4.png",
]

main_font_name = "Jura.ttf"
main_font_path = FONTS_DIR + main_font_name

icon_path = os.path.join(SYSTEM_IMAGES_DIR, SYSTEM_IMAGE_FILES[0])

IF_TEST_STRUCTURE = True
