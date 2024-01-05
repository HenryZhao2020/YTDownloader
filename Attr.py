"""
Contains the implementation of the 'Attribute' class.
"""

import os
import pickle

from MyTube import Option, Quality


class Attribute:
    """
    Stores attributes for saving and loading game state.
    """

    def __init__(self):
        self.opt: str
        self.resPref: str
        self.abrPref: str
        self.dir: str

        # Set all attributes to their default values
        self.reset()

    def reset(self):
        """
        Resets all attributes to their default values.
        """

        self.opt = Option.VideoWithAudio
        self.resPref = Quality.Highest
        self.abrPref = Quality.Highest
        self.dir = os.path.expanduser("~")

    def save(self):
        """
        Saves all attributes in "__init__" to the local disk.
        """
        
        with open("../Saved", "wb") as file:
            pickle.dump(vars(self), file)

    def load(self):
        """
        Loads all attributes in "__init__" from the local disk.
        """

        with open("../Saved", "rb") as file:
            vars(self).update(pickle.load(file))


# Create a singleton for the Attribute class
attr = Attribute()
