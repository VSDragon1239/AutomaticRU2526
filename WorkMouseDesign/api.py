from PySide6.QtGui import QColor

from WorkMouseDesign.App.CursorOverlay import CursorPetOverlay
from WorkMouseDesign.settings import SourceDataDir


def WorkMouseDesignApi():
    pet = CursorPetOverlay()

    # Состояние "idle"
    pet.register_state(
        "idle",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        color=QColor(255, 255, 0, 0),
        size=(100, 100),
        offset=(15, 35),
        rotation=0
    )

    pet.register_state(
        "move_left",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        size=(100, 100),
        offset=(15, 35),
    )

    pet.register_state(
        "move_right",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        size=(100, 100),
        offset=(-120, 35),
    )

    # Состояние "move_up"
    pet.register_state(
        "move_up",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        color=QColor(255, 255, 0, 0),
        size=(100, 100),
        offset=(15, 35),
        rotation=0
    )

    # Состояние "move_down"
    pet.register_state(
        "move_down",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        color=QColor(255, 255, 0, 0),
        size=(100, 100),
        offset=(15, -70),
        rotation=0
    )

    pet.register_state(
        "play",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        color=QColor(255, 0, 255, 0),
        size=(100, 100),
        offset=(0, 30),
    )

    # При желании — спец состояния для настроений:
    pet.register_state(
        "sleep",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        size=(100, 100),
        offset=(0, 40),
    )

    pet.register_state(
        "bored",
        image_path=SourceDataDir + "flattershy_alicorn.gif",
        size=(100, 100),
        offset=(0, 35),
    )

    # pet.register_state(
    #     "happy",
    #     image_path=SourceDataDir + "flattershy_alicorn.gif",
    #     size=(100, 100),
    #     offset=(15, 35),
    # )

    pet.show()
    return pet
