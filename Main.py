import Preparator
import GUI
import sys
from PyQt5.QtWidgets import QApplication


def start_application():
    # Preparing folders
    Preparator.Preparator()

    # Calling the GUI
    app = QApplication(sys.argv)
    gui = GUI.MyWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_application()


