from abc import ABC, abstractmethod


class State(ABC):
    """
    TODO: finish
    """

    def __init__(self):
        pass

    @classmethod
    def make_from(cls, other):
        return cls(other.x, other.y, other.z)  # fill this out with actual instance variables

    @abstractmethod
    async def loop(self):
        """
        This method is run every time the main thread loops.
        """
