import sys
from PySide6.QtWidgets import QApplication

from WorkMouseDesign.App.CursorOverlay import CursorPetOverlay


def main():
    app = QApplication(sys.argv)

    overlay = CursorPetOverlay()
    overlay.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
