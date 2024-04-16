"""
Contains the implementation of the main window.
"""

import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QMessageBox, QPushButton, QSpacerItem, QWidget,
)
from pytube import YouTube, Playlist

import MyTube
import Thread


class MainWindow(QMainWindow):
    """
    Prompts the user to enter the URL of a video or a playlist,
    then proceeds to download.
    """

    def __init__(self):
        super().__init__()

        # Display a menu bar on the top
        menuBar = MenuBar(self)
        self.setMenuBar(menuBar)

        # Create a central widget
        widget = QWidget(self)
        self.setCentralWidget(widget)

        # Set up the layout
        gridLayout = QGridLayout(widget)
        gridLayout.setSpacing(8)
        gridLayout.setContentsMargins(40, 40, 40, 40)

        # Prompt the user to enter the URL
        promptLabel = QLabel("Enter Video or Playlist URL:", self)
        gridLayout.addWidget(promptLabel, 0, 0, 1, 2)

        # Create a field for entering the URL
        self.urlField = QLineEdit(self)
        self.urlField.setMinimumWidth(360)
        self.urlField.returnPressed.connect(lambda: self.nextButton.click())
        self.urlField.textChanged.connect(lambda: (
            self.resetStatus(),
            Thread.start(lambda: self.checkUrl()),
        ))
        gridLayout.addWidget(self.urlField, 1, 0)

        # Set URL to the content of the clipboard
        pasteButton = QPushButton("Paste", self)
        pasteButton.setToolTip("Set URL to the content of the clipboard")
        pasteButton.clicked.connect(lambda: (
            self.urlField.setText(QApplication.clipboard().text()),
            self.nextButton.click(),
        ))
        gridLayout.addWidget(pasteButton, 1, 1)

        # Display status while entering the URL
        self.infoLabel = QLabel(self)
        gridLayout.addWidget(self.infoLabel, 2, 0, 1, 2)

        # Proceed to download on click
        self.nextButton = QPushButton("Next", self)
        self.nextButton.setDefault(True)
        self.nextButton.setEnabled(False)
        self.nextButton.clicked.connect(lambda: self.next())
        gridLayout.addItem(QSpacerItem(0, 32), 3, 1)
        gridLayout.addWidget(self.nextButton, 4, 1, Qt.AlignmentFlag.AlignRight)

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

        # If URL is invalid, display an error message in red
        if error := MyTube.checkUrl(url):
            self.infoLabel.setText(error)
            self.infoLabel.setStyleSheet("color: red")
            return

        # If URL is a valid video or playlist, display a message in green
        if MyTube.isUrlPlaylist(url):
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

        # NOTE: place the import statement here to avoid circular import
        from Dialog import VideoDialog, PlaylistDialog

        # Entered URL
        url = self.urlField.text()

        # Download playlist
        # Ex: https://www.youtube.com/playlist?list=PL6C1LEYvl43RHLS2gFFf6kn4hoAs6kOgF
        if MyTube.isUrlPlaylist(url):
            dialog = PlaylistDialog(self, url)

        # If a video is part of a playlist, prompt user to choose 
        # between downloading the single video or the entire playlist
        # Ex: https://youtu.be/KWLGyeg74es?list=PL6C1LEYvl43RHLS2gFFf6kn4hoAs6kOgF
        elif not MyTube.checkPlaylistUrl(MyTube.extractPlaylistUrl(url)):
            ans = QMessageBox.question(
                self, "Video or Playlist", 
                "This video is part of a playlist.\n"
                "Do you want to download the playlist instead?"
            )

            if ans == QMessageBox.StandardButton.Yes:
                id = url[url.index('list'):]
                url = f"https://www.youtube.com/playlist?{id}"
                dialog = PlaylistDialog(self, url)
            else:
                dialog = VideoDialog(self, url)
    
        # Download video
        # Ex: https://youtu.be/KWLGyeg74es
        else:
            dialog = VideoDialog(self, url)

        dialog.show()
        # Fetch information
        dialog.startFetch()

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

        # NOTE: place the import statement here to avoid circular import
        from Dialog import PrefDialog, AboutDialog

        # Create the 'File' menu
        fileMenu = self.addMenu("&File")
        fileMenu.addAction("&Preferences", "Ctrl+P", 
                           lambda: PrefDialog(win).show())
        fileMenu.addAction("Visit &YouTube", 
                           lambda: webbrowser.open("https://www.youtube.com"))
        fileMenu.addSeparator()
        fileMenu.addAction("E&xit", lambda: QApplication.quit())

        # Create the 'Help' menu
        helpMenu = self.addMenu("&Help")
        helpMenu.addAction("&About YT Downloader", "F1",
                           lambda: AboutDialog(win).show())
