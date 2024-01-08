"""
Simplified implementation of threading in Qt.
"""

from typing import Callable

from PySide6.QtCore import QThread


def start(run: Callable, finished=lambda: None):
    """
    Creates and starts a thread.
    """

    thread = QThread()
    thread.run = lambda: (run(), thread.finished.emit())
    thread.finished.connect(finished)
    thread.start()
