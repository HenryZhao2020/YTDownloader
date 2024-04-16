"""
Contains the implementation of the 'Attr' class.
"""

import os
import pickle

from MyTube import Option, Quality


class Attr:
    """
    Contains shared attributes for saving and loading program state.
    """

    def __init__(self):
        # Default download option
        self.opt = Option.VideoWithAudio
        # Default video quality
        self.vidQuality = Quality.Highest
        # Default audio quality
        self.audQuality = Quality.Highest
        # Default download location
        self.dir = os.path.expanduser("~")
        # Whether to confirm before download
        self.confirmDownload = True
        # Whether to close dialog after download
        self.closeAfterDownload = False

    def resetAll(self):
        """
        Resets all attributes to their default values.
        """

        self.__init__()

    def save(self):
        """
        Saves all attributes to the local disk.
        """
        
        with open("../Saved", "wb") as file:
            pickle.dump(vars(self), file)

    def load(self):
        """
        Loads all attributes from the local disk.
        """

        with open("../Saved", "rb") as file:
            vars(self).update(pickle.load(file))


# Create a singleton for the 'Attr' class
attr = Attr()
