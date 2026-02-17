import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from WorkMouseDesign.App.CursorOverlay import CursorPetOverlay
from WorkMouseDesign.settings import SourceDataDir


def demo():
    app = QApplication(sys.argv)

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

    # Для демонстрации: циклически переключаем состояния
    # from PySide6.QtCore import QTimer
    #
    # states = ["idle", "move", "big_red"]
    # idx = {"value": 0}
    #
    # def switch_state():
    #     idx["value"] = (idx["value"] + 1) % len(states)
    #     pet.set_state(states[idx["value"]])
    #     print(states[idx["value"]])
    #
    # switch_timer = QTimer()
    # switch_timer.setInterval(5000)  # раз в секунду
    # switch_timer.timeout.connect(switch_state)
    # switch_timer.start()
    # pet.set_state(states[1])

    sys.exit(app.exec())


if __name__ == "__main__":
    demo()
