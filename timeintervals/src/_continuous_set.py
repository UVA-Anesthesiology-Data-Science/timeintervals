"""A module that contains the definition of the ContinuousSet protocol."""

from abc import abstractmethod
from typing import Protocol
from typing_extensions import Self


class ContinuousSet(Protocol):
    """A protocol for classes that reflect sets of continuous elements."""
    
    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other) -> Self:
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other) -> Self:
        raise NotImplementedError
