"""
Executes the main program.
"""

import os

# Set the current directory to 'Res'
# NOTE: place the following codes before importing 'gui'
try:
    os.chdir(os.path.dirname(__file__))
    os.chdir("Res")
except Exception:
    raise SystemExit("Cannot locate the required resource files.")

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from mainwindow import MainWindow
from attr import attr


def main():
    """
    Sets up the application, then starts the program.
    """
    
    # Create a new 'QApplication' instance
    app = QApplication([])
    app.setApplicationName("YT Downloader")
    app.setWindowIcon(QIcon("Logo.png"))

    # Save attributes upon exiting the program
    app.aboutToQuit.connect(lambda: attr.save())

    # Load external style sheet
    with open("Styles.qss") as file:
        app.setStyleSheet(file.read())

    # Load attributes if possible
    try:
        attr.load()
    except Exception:
        ...

    # Create a new 'MainWindow' instance
    win = MainWindow()
    win.show()

    # Execute the program
    app.exec()


if __name__ == "__main__":
    main()
