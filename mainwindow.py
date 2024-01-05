"""
Contains the GUI implementation.
"""

import webbrowser

from pytube import YouTube, Playlist
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QMenuBar, \
    QLabel, QLineEdit, QSpacerItem, QPushButton

import mytube
import thread


class MainWindow(QMainWindow):
    """
    Prompts the user to enter a URL, then proceeds to download.
    """

    def __init__(self):
        super().__init__()

        # Create a central widget
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # Display a menu bar on the top
        menu = MenuBar(self)
        self.setMenuBar(menu)

        # Set up the layout
        gridLayout = QGridLayout(widget)
        gridLayout.setHorizontalSpacing(50)
        gridLayout.setVerticalSpacing(5)
        gridLayout.setContentsMargins(40, 40, 40, 40)

        # Create a field for entering the URL
        self.urlField = QLineEdit(self)
        self.urlField.setMinimumWidth(350)
        self.urlField.textChanged.connect(lambda: (
            self.resetStatus(),
            thread.start(lambda: self.checkUrl()),
        ))
        self.urlField.returnPressed.connect(lambda: self.nextButton.click())
        gridLayout.addWidget(QLabel("URL:", self), 0, 0)
        gridLayout.addWidget(self.urlField, 0, 1)

        # Display status while entering the URL
        self.infoLabel = QLabel(self)
        gridLayout.addWidget(self.infoLabel, 1, 1, Qt.AlignmentFlag.AlignTop)

        # Proceed to download on click
        self.nextButton = QPushButton("Next", self)
        self.nextButton.setDefault(True)
        self.nextButton.setEnabled(False)
        self.nextButton.clicked.connect(lambda: self.next())
        gridLayout.addItem(QSpacerItem(0, 25), 2, 1)
        gridLayout.addWidget(self.nextButton, 3, 1, 
                             Qt.AlignmentFlag.AlignRight)

    def resetStatus(self):
        """
        Resets the status before checking URL.
        """

        self.infoLabel.setText("")
        self.nextButton.setEnabled(False)

    def checkUrl(self):
        """
        Checks the status while entering the URL.
        """

        # Entered URL
        url = self.urlField.text()

        # If URL is empty, skip check
        if not url:
            return

        # If URL is invalid, display an error message
        if (error := mytube.check_url(url)):
            self.infoLabel.setText(error)
            self.infoLabel.setStyleSheet("color: red")
            return

        # If URL is a valid video or playlist, notify the user
        if mytube.is_url_playlist(url):
            pl = Playlist(url)
            self.infoLabel.setText(f'Playlist: {pl.title}')
        else:
            yt = YouTube(url)
            self.infoLabel.setText(f'Video: {yt.title}')

        self.infoLabel.setStyleSheet("color: green")
        self.nextButton.setEnabled(True)

    def next(self):
        """
        If URL is valid, proceed to download.
        """

        # NOTE: place the statement here to avoid circular import
        from dialog import VideoDialog, PlaylistDialog

        # Entered URL
        url = self.urlField.text()

        # Switch to the download dialog
        if mytube.is_url_playlist(url):
            dialog = PlaylistDialog(self, url)
        else:
            dialog = VideoDialog(self, url)

        # Fetch information
        dialog.show()
        dialog.preFetch()
        thread.start(lambda: dialog.fetch(),
                     lambda: dialog.postFetch())

    def show(self):
        """
        Overrides the original show() method.
        """

        # Make this window not resizable
        self.setFixedSize(self.sizeHint())
        super().show()


class MenuBar(QMenuBar):
    """
    File | Help
    """

    def __init__(self, win: MainWindow):
        super().__init__(win)

        from dialog import PrefDialog, AboutDialog

        # Create the 'File' menu
        fileMenu = self.addMenu("&File")
        fileMenu.addAction("&Preferences", "Ctrl+P", 
                           lambda: PrefDialog(win).show())
        fileMenu.addAction("&Go to YouTube", 
                           lambda: webbrowser.open("https://www.youtube.com"))
        fileMenu.addSeparator()
        fileMenu.addAction("E&xit", lambda: QApplication.quit())

        # Create the 'Help' menu
        helpMenu = self.addMenu("&Help")
        helpMenu.addAction("&About YT Downloader", "F1",
                           lambda: AboutDialog(win).show())
