import Preparator
from gui import MainWindow
import sys
from PyQt5.QtWidgets import QApplication


def start_application():
    # Preparing folders
    Preparator.Preparator()

    # Calling the GUI
    app = QApplication(sys.argv)
    gui = MainWindow.MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_application()