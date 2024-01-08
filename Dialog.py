"""
Contains the implementation of various dialog boxes used in the program.
"""

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, \
    QGridLayout
from PySide6.QtWidgets import QWidget, QDialog, QFileDialog, QMessageBox, \
    QFrame, QPushButton, QGroupBox, QLineEdit, QComboBox, QCheckBox, \
    QListWidget, QListWidgetItem, QTextBrowser
from pytube import YouTube, Playlist

import MyTube
import Thread
from Attr import attr
from MainWindow import MainWindow
from MyTube import Option


class DownloadDialog(QDialog):
    """
    Base class for the 'VideoDialog' class and the 'PlaylistDialog' class.
    """

    def __init__(self, win: MainWindow):
        super().__init__(win)
        # Free memory on close
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(25)
        self.mainLayout.setContentsMargins(40, 40, 40, 40)

        # Configure download quality
        self.qualFrame = QualityFrame(self)
        self.mainLayout.addWidget(newGroupBox("Quality", self, self.qualFrame))

        # Configure download location
        self.dirFrame = DirFrame(self)
        self.mainLayout.addWidget(newGroupBox("Save To", self, self.dirFrame))

        # Start downloading on click
        self.startButton = QPushButton("Start", self)
        self.startButton.setDefault(True)
        self.startButton.clicked.connect(lambda: self.confirmDownload())
        self.mainLayout.addSpacing(25)
        self.mainLayout.addWidget(self.startButton, 0,
                                  Qt.AlignmentFlag.AlignRight)

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

    def postFetch(self):
        """
        Handles events after fetching completes.
        """

        self.setEnabled(True)

    def confirmDownload(self):
        """
        Confirms before downloading.
        """

        # Confirm before download if preferred
        if attr.confirmDownload:
            # Display a question message box
            ans = QMessageBox.question(self, "Confirm Download",
                                       "Do you want to start the download?")

            # If the user does not select 'Yes', cancel download
            if ans != QMessageBox.StandardButton.Yes:
                return

        # Otherwise, proceed to download
        self.preDownload(),
        Thread.start(lambda: self.download(),
                     lambda: self.postDownload())

    def preDownload(self):
        """
        Handles events before downloading.
        """

        # Disable the dialog to prevent any configurations from changing
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

        # Close the dialog after download if preferred
        if attr.closeAfterDownload:
            self.close()
            return

        # Enable the dialog again
        self.setEnabled(True)
        self.setWindowTitle("Download Complete!")

    def show(self):
        """
        Overrides the original show() method.
        """

        size = self.sizeHint()
        # Calculate the dialog width based on the dialog height
        size.setWidth(round(size.height() * 0.85))
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
        # If option is 'Audio Only', disable selection of resolutions
        # If option is 'Video Only', disable selection of bitrates
        self.optBox.addItems(MyTube.OPTIONS)
        self.optBox.currentTextChanged.connect(lambda opt: (
            self.vidBox.setEnabled(opt != Option.AudioOnly),
            self.audBox.setEnabled(opt != Option.VideoOnly),
        ))
        formLayout.addRow("Option:", self.optBox)

        # Display and select video resolution
        self.vidBox = QComboBox(self)
        self.vidBox.addItems(MyTube.QUALITIES)
        formLayout.addRow("Video Quality:", self.vidBox)

        # Display and select audio bitrate
        self.audBox = QComboBox(self)
        self.audBox.addItems(MyTube.QUALITIES)
        formLayout.addRow("Audio Quality:", self.audBox)

        # Set to default
        self.optBox.setCurrentText(attr.opt)
        self.vidBox.setCurrentText(attr.vidQuality)
        self.audBox.setCurrentText(attr.audQuality)

    def opt(self):
        """
        Returns the selected download option.
        """

        return self.optBox.currentText()

    def vidQuality(self):
        """
        Returns the selected video quality.
        """

        return self.vidBox.currentText()

    def audQuality(self):
        """
        Returns the selected audio quality.
        """

        return self.audBox.currentText()


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
        super().__init__(win)

        # Create a 'YouTube' instance
        self.yt = YouTube(url)

        # Display and edit video title
        self.titleField = QLineEdit(self)
        self.mainLayout.insertWidget(
            0, newGroupBox("Title", self, self.titleField)
        )

    def fetch(self):
        super().fetch()

        self.titleField.setText(self.yt.title)

        self.qualFrame.vidBox.addItems(MyTube.allResolutions(self.yt))
        self.qualFrame.audBox.addItems(MyTube.allBitrates(self.yt))

    def postFetch(self):
        super().postFetch()

        self.setWindowTitle("Download Video")

    def download(self):
        super().download()

        # Fetch configurations
        title = self.titleField.text()
        opt = self.qualFrame.opt()
        vidQuality = self.qualFrame.vidQuality()
        audQuality = self.qualFrame.audQuality()
        res = MyTube.getResolution(self.yt, vidQuality)
        abr = MyTube.getBitrate(self.yt, audQuality)
        dir = self.dirFrame.dir()

        # Download the video according to the configurations
        if opt == Option.VideoWithAudio:
            MyTube.downloadBoth(self.yt, title, res, abr, dir)
        elif opt == Option.AudioOnly:
            MyTube.downloadAudio(self.yt, title, abr, dir)
        else:
            MyTube.downloadVideo(self.yt, title, res, dir)

    def postDownload(self):
        super().postDownload()

        # Reset the window title after 10s
        QTimer.singleShot(10000, self,
                          lambda: self.setWindowTitle("Download Video"))


class PlaylistDialog(DownloadDialog):
    """
    Configures playlist information before downloading.
    """

    def __init__(self, win: MainWindow, url: str):
        super().__init__(win)

        # Create a 'Playlist' instance
        self.pl = Playlist(url)

        # Display all videos inside a playlist
        self.listWidget = QListWidget(self)
        # Disable the 'Start' button if no item is selected
        self.listWidget.itemChanged.connect(
            lambda: self.startButton.setDisabled(not self.getCheckedRows())
        )
        self.mainLayout.insertWidget(
            0, newGroupBox("Playlist", self, self.listWidget)
        )

    def fetch(self):
        super().fetch()

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

    def getCheckedRows(self):
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
        rows = self.getCheckedRows()
        opt = self.qualFrame.opt()
        vidQuality = self.qualFrame.vidQuality()
        audQuality = self.qualFrame.audQuality()
        dir = self.dirFrame.dir()

        for i, row in enumerate(rows):
            self.setWindowTitle(f"Downloading ({i + 1} of {len(rows)})...")

            # Fetch configurations
            yt = self.pl.videos[i]
            title = self.listWidget.item(row).text()
            res = MyTube.getResolution(yt, vidQuality)
            abr = MyTube.getBitrate(yt, audQuality)

            # Download the video according to the configurations
            if opt == Option.VideoWithAudio:
                MyTube.downloadBoth(yt, title, res, abr, dir)
            elif opt == Option.AudioOnly:
                MyTube.downloadAudio(yt, title, abr, dir)
            else:
                MyTube.downloadVideo(yt, title, res, dir)

    def postDownload(self):
        super().postDownload()

        # Reset the window title after 10s
        QTimer.singleShot(10000, self,
                          lambda: self.setWindowTitle("Download Playlist"))


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
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(25)
        mainLayout.setContentsMargins(40, 40, 40, 40)

        # Configure download quality
        self.qualFrame = QualityFrame(self)
        mainLayout.addWidget(newGroupBox("Quality", self, self.qualFrame))

        # Configure download location
        self.dirFrame = DirFrame(self)
        mainLayout.addWidget(newGroupBox("Save To", self, self.dirFrame))

        # Whether to confirm before download
        self.confirmBox = QCheckBox("Confirm Before Download", self)
        self.confirmBox.setChecked(attr.confirmDownload)

        # Whether to close dialog after download
        self.closeAfterBox = QCheckBox("Close Dialog After Download", self)
        self.closeAfterBox.setChecked(attr.closeAfterDownload)

        # Group all check boxes
        mainLayout.addWidget(newGroupBox("Action", self,
                                         self.confirmBox,
                                         self.closeAfterBox))

        # Display buttons horizontally
        buttonFrame = QFrame(self)
        mainLayout.addSpacing(25)
        mainLayout.addWidget(buttonFrame)

        buttonLayout = QHBoxLayout(buttonFrame)
        buttonLayout.setSpacing(5)
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        # Reset all preferences on click
        resetButton = QPushButton("Reset", self)
        resetButton.clicked.connect(lambda: (
            attr.resetAll(),
            self.close(),
        ))
        buttonLayout.addWidget(resetButton)
        buttonLayout.addStretch()

        # Apply changes on click
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
        Applies settings.
        """

        attr.opt = self.qualFrame.opt()
        attr.vidQuality = self.qualFrame.vidQuality()
        attr.audQuality = self.qualFrame.audQuality()
        attr.dir = self.dirFrame.dir()
        attr.confirmDownload = self.confirmBox.isChecked()
        attr.closeAfterDownload = self.closeAfterBox.isChecked()

    def show(self):
        """
        Overrides the original show() method.
        """

        size = self.sizeHint()
        # Calculate the dialog width based on the dialog height
        size.setWidth(round(size.height() * 0.85))
        # Make this window not resizable
        self.setFixedSize(size)
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


def newGroupBox(title: str, parent: QWidget = None, *widgets: QWidget):
    """
    Creates a group box with a vertical box layout.
    """

    box = QGroupBox(title, parent)

    # Set up the layout
    vboxLayout = QVBoxLayout(box)
    vboxLayout.setSpacing(5)
    vboxLayout.setContentsMargins(25, 25, 25, 25)

    # Add widgets to layout
    for widget in widgets:
        vboxLayout.addWidget(widget)

    return box
