"""
Contains the implementation of various dialog boxes used in the program.
"""

from pytube import YouTube, Playlist
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, \
    QGridLayout
from PySide6.QtWidgets import QWidget, QDialog, QFileDialog, QMessageBox, \
    QFrame, QPushButton, QLabel, QGroupBox, QLineEdit, QComboBox, \
    QSpacerItem, QListWidget, QListWidgetItem, QTextBrowser

import mytube
import thread
from mainwindow import MainWindow
from mytube import Option
from attr import attr


class DownloadDialog(QDialog):
    """
    Base class for the 'VideoDialog' class and the 'PlaylistDialog' class.
    """

    def __init__(self, win: MainWindow, width: int):
        super().__init__(win)
        # Free memory on close
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.fixedWidth = width

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(25)
        self.mainLayout.setContentsMargins(40, 40, 40, 40)

        # Configure video quality
        self.qualFrame = QualityFrame(self)
        self.mainLayout.addWidget(self.newGroupBox("Quality", self.qualFrame))
        
        # Download location
        self.dirFrame = DirFrame(self)
        self.mainLayout.addWidget(self.newGroupBox("Location", self.dirFrame))

        # Start downloading on click
        self.startButton = QPushButton("Start", self)
        self.startButton.setDefault(True)
        self.startButton.clicked.connect(lambda: self.confirmDownload())
        self.mainLayout.addSpacing(25)
        self.mainLayout.addWidget(self.startButton, 0,
                                  Qt.AlignmentFlag.AlignRight)

    def newGroupBox(self, title: str, *widgets: QWidget):
        """
        Creates a group box with the specified title and widgets.
        """

        box = QGroupBox(title, self)
        
        # Set up the layout
        vboxLayout = QVBoxLayout(box)
        vboxLayout.setSpacing(0)
        vboxLayout.setContentsMargins(25, 25, 25, 25)
        
        # Add widgets to layout
        for widget in widgets:
            vboxLayout.addWidget(widget)

        return box

    def preFetch(self):
        """
        Handles events before fetching.
        """

        self.setEnabled(False)
        self.setWindowTitle("Fetching Information...")

    def fetch(self):
        """
        Fetches information online.
        """

        self.qualFrame.optBox.addItems(mytube.OPTIONS)

    def postFetch(self):
        """
        Handles events after fetching completes.
        """

        self.setEnabled(True)

        self.qualFrame.optBox.setCurrentText(attr.opt)

    def confirmDownload(self):
        """
        Confirms before downloading.
        """

        ans = QMessageBox.question(self, "Confirm Download", 
                                   "Do you want to start the download?")
        
        if ans == QMessageBox.StandardButton.Yes:
            self.preDownload(),
            thread.start(lambda: self.download(),
                         lambda: self.postDownload())

    def preDownload(self):
        """
        Handles events before downloading.
        """

        self.setEnabled(False)
        self.setWindowTitle("Downloading...")

    def download(self):
        """
        Starts downloading.
        """

    def postDownload(self):
        """
        Handles events after downloading.
        """

        self.setEnabled(True)
        self.setWindowTitle("Download Complete!")

    def show(self):
        """
        Overrides the original show() method.
        """

        # Set fixed width
        size = self.sizeHint()
        size.setWidth(self.fixedWidth)
        # Make this window not resizable
        self.setFixedSize(size)
        super().show()


class QualityFrame(QFrame):
    """
    Displays and selects the quality.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Set up the layout
        formLayout = QFormLayout(self)
        formLayout.setHorizontalSpacing(40)
        formLayout.setVerticalSpacing(5)
        formLayout.setContentsMargins(0, 0, 0, 0)

        # Display and select download option
        self.optBox = QComboBox(self)
        # If option is 'Audio Only', disable selection of resolution
        # If option is 'Video Only', disable selection of bitrate
        self.optBox.currentTextChanged.connect(lambda opt: (
            self.resBox.setEnabled(opt != Option.AudioOnly),
            self.abrBox.setEnabled(opt != Option.VideoOnly),
        ))
        formLayout.addRow("Option:", self.optBox)

        # Display and select video resolution
        self.resBox = QComboBox(self)
        formLayout.addRow("Video Resolution:", self.resBox)

        # Display and select audio bitrate
        self.abrBox = QComboBox(self)
        formLayout.addRow("Audio Bitrate:", self.abrBox)


class DirFrame(QFrame):
    """
    Displays and edits the download directory.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Set up the layout
        hboxLayout = QHBoxLayout(self)
        hboxLayout.setSpacing(5)
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # Display and edit directory
        self.dirField = QLineEdit(attr.dir, self)
        hboxLayout.addWidget(self.dirField)

        # Open a file dialog for selecting a directory on click
        browseButton = QPushButton("Browse", self)
        browseButton.clicked.connect(lambda: self.browse())
        hboxLayout.addWidget(browseButton)

    def dir(self):
        """
        Returns the text inside the directory field.
        """

        return self.dirField.text()

    def browse(self):
        """
        Opens a file dialog for selecting a directory.
        """

        # Select a new directory
        dir = QFileDialog.getExistingDirectory(self, dir=self.dirField.text())
        # Make sure the selection is not empty
        if dir:
            self.dirField.setText(dir)


class VideoDialog(DownloadDialog):
    """
    Configures video information before downloading.
    """

    def __init__(self, win: MainWindow, url: str):
        super().__init__(win, 450)

        # Create a 'YouTube' instance
        self.yt = YouTube(url)

        # Display and edit video title
        self.titleField = QLineEdit(self)
        self.mainLayout.insertWidget(
            0, self.newGroupBox("Title", self.titleField)
        )

    def fetch(self):
        super().fetch()

        self.titleField.setText(self.yt.title)
        self.qualFrame.resBox.addItems(mytube.get_resolutions(self.yt))
        self.qualFrame.abrBox.addItems(mytube.get_bitrates(self.yt))

    def postFetch(self):
        super().postFetch()
    
        self.setWindowTitle("Download Video")

        # Set default resolution
        res = mytube.get_quality(attr.resPref, mytube.get_resolutions(self.yt))
        self.qualFrame.resBox.setCurrentText(res)

        # Set default bitrate
        abr = mytube.get_quality(attr.abrPref, mytube.get_bitrates(self.yt))
        self.qualFrame.abrBox.setCurrentText(abr)

    def download(self):
        super().download()

        # Fetch configurations
        title = self.titleField.text()
        opt = self.qualFrame.optBox.currentText()
        res = self.qualFrame.resBox.currentText()
        abr = self.qualFrame.abrBox.currentText()
        dir = self.dirFrame.dir()

        # Download the video according to the configurations
        if opt == Option.VideoWithAudio:
            mytube.download_both(self.yt, title, res, abr, dir)
        elif opt == Option.AudioOnly:
            mytube.download_audio(self.yt, title, abr, dir)
        else:
            mytube.download_video(self.yt, title, res, dir)


class PlaylistDialog(DownloadDialog):
    """
    Configures playlist information before downloading.
    """

    def __init__(self, win: MainWindow, url: str):
        super().__init__(win, 550)

        # Create a 'Playlist' instance
        self.pl = Playlist(url)

        # Display all videos inside a playlist
        self.listWidget = QListWidget(self)
        self.mainLayout.insertWidget(
            0, self.newGroupBox("Playlist", self.listWidget)
        )

    def fetch(self):
        super().fetch()

        self.qualFrame.resBox.addItems(mytube.QUALITIES)
        self.qualFrame.abrBox.addItems(mytube.QUALITIES)

        # Fetch all videos
        for yt in self.pl.videos:
            self.addPlaylistItem(yt)

    def addPlaylistItem(self, yt: YouTube):
        """
        Adds an item to the playlist.
        """

        item = QListWidgetItem(yt.title, self.listWidget)
        item.setCheckState(Qt.CheckState.Checked)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | 
                      Qt.ItemFlag.ItemIsEditable |
                      Qt.ItemFlag.ItemIsSelectable |
                      Qt.ItemFlag.ItemIsUserCheckable)
        self.listWidget.addItem(item)

    def postFetch(self):
        super().postFetch()

        self.setWindowTitle("Download Playlist")

        self.qualFrame.resBox.setCurrentText(attr.resPref)
        self.qualFrame.abrBox.setCurrentText(attr.abrPref)

    def checkedRows(self):
        """
        Returns the row numbers of all checked items. 
        """

        return [
            i for i in range(self.listWidget.count()) 
            if self.listWidget.item(i).checkState() == Qt.CheckState.Checked
        ]

    def download(self):
        super().download()

        # Total number of videos in a playlist
        rows = self.checkedRows()
        opt = self.qualFrame.optBox.currentText()
        resPref = self.qualFrame.resBox.currentText()
        abrPref = self.qualFrame.abrBox.currentText()
        dir = self.dirFrame.dir()
        
        for i, row in enumerate(rows):
            self.setWindowTitle(f"Downloading ({i + 1} of {len(rows)})...")

            # Fetch configurations
            yt = self.pl.videos[row]
            title = self.listWidget.item(row).text()
            res = mytube.get_quality(resPref, mytube.get_resolutions(yt))
            abr = mytube.get_quality(abrPref, mytube.get_bitrates(yt))

            # Download the video according to the configurations
            if opt == Option.VideoWithAudio:
                mytube.download_both(yt, title, res, abr, dir)
            elif opt == Option.AudioOnly:
                mytube.download_audio(yt, title, abr, dir)
            else:
                mytube.download_video(yt, title, res, dir)


class PrefDialog(QDialog):
    """
    Displays and edits user preferences.
    """

    def __init__(self, win: MainWindow):
        super().__init__(win)
        self.setWindowTitle("Preferences")
        # Free memory on close
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Set up the layout
        gridLayout = QGridLayout(self)
        gridLayout.setHorizontalSpacing(40)
        gridLayout.setVerticalSpacing(5)
        gridLayout.setContentsMargins(40, 40, 40, 40)

        # Default download option
        self.optBox = QComboBox(self)
        self.optBox.setMinimumWidth(260)
        self.optBox.addItems(mytube.OPTIONS)
        self.optBox.setCurrentText(attr.opt)
        gridLayout.addWidget(QLabel("Default Option:", self), 0, 0)
        gridLayout.addWidget(self.optBox, 0, 1)

        # Default video quality
        self.resBox = QComboBox(self)
        self.resBox.addItems(mytube.QUALITIES)
        self.resBox.setCurrentText(attr.resPref)
        gridLayout.addWidget(QLabel("Preferred Resolution:", self), 1, 0)
        gridLayout.addWidget(self.resBox, 1, 1)

        # Default audio quality
        self.abrBox = QComboBox(self)
        self.abrBox.addItems(mytube.QUALITIES)
        self.abrBox.setCurrentText(attr.abrPref)
        gridLayout.addWidget(QLabel("Preferred Bitrate:", self), 2, 0)
        gridLayout.addWidget(self.abrBox, 2, 1)

        # Default download directory
        self.dirFrame = DirFrame(self)
        gridLayout.addWidget(QLabel("Default Location:", self), 3, 0)
        gridLayout.addWidget(self.dirFrame, 3, 1)
        gridLayout.addItem(QSpacerItem(0, 50), 4, 0)

        # Create a button group
        buttonFrame = QFrame(self)
        gridLayout.addWidget(buttonFrame, 5, 0, 1, 2)

        # Display button horizontally
        buttonLayout = QHBoxLayout(buttonFrame)
        buttonLayout.setSpacing(5)
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        # Reset all preferences on click
        resetButton = QPushButton("Reset", self)
        resetButton.clicked.connect(lambda: (
            attr.reset(),
            self.close(),
        ))
        buttonLayout.addWidget(resetButton)
        buttonLayout.addStretch()

        # Apply preferences on click
        okButton = QPushButton("OK", self)
        okButton.setDefault(True)
        okButton.clicked.connect(lambda: (
            self.apply(),
            self.close(),
        ))
        buttonLayout.addWidget(okButton)

        # Discard changes on click
        cancelButton = QPushButton("Cancel", self)
        cancelButton.clicked.connect(lambda: self.close())
        buttonLayout.addWidget(cancelButton)

    def apply(self):
        """
        Applys preferences.
        """

        attr.opt = self.optBox.currentText()
        attr.resPref = self.resBox.currentText()
        attr.abrPref = self.abrBox.currentText()
        attr.dir = self.dirFrame.dirField.text()

    def show(self):
        """
        Overrides the original show() method.
        """

        # Make this window not resizable
        self.setFixedSize(self.sizeHint())
        super().show()


class AboutDialog(QDialog):
    """
    Displays information about this program.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("About")
        # Free memory on close
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Set up the layout
        gridLayout = QGridLayout(self)
        gridLayout.setHorizontalSpacing(25)
        gridLayout.setVerticalSpacing(40)
        gridLayout.setContentsMargins(40, 40, 40, 40)

        # Display logo on the left
        logoButton = QPushButton(self)
        logoButton.setIcon(QIcon("Logo.png"))
        logoButton.setIconSize(QSize(128, 128))
        logoButton.setStyleSheet("border: 0")
        gridLayout.addWidget(logoButton, 0, 0)

        # Display HTML on the right
        browser = QTextBrowser(self)
        # Open hyperlinks in the HTML content on click
        browser.setOpenExternalLinks(True)
        browser.anchorClicked.connect(lambda: ...)
        gridLayout.addWidget(browser, 0, 1)

        # Display HTML content
        with open("About.html") as file:
            browser.setHtml(file.read())

        # Close the dialog on close
        okButton = QPushButton("OK", self)
        okButton.setDefault(True)
        okButton.clicked.connect(lambda: self.close())
        gridLayout.addWidget(okButton, 1, 1, Qt.AlignmentFlag.AlignRight)

    def show(self):
        """
        Overrides the original show() method.
        """

        # Make this window not resizable
        self.setFixedSize(self.sizeHint())
        super().show()
