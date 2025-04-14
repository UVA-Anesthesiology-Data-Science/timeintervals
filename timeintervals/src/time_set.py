"""A module defining the TimeSet class, a set of TimeIntervals."""

from .time_interval import TimeInterval
from typing import List, Optional, Union
from typing_extensions import Self


class TimeSet:
    """A set of TimeIntervals that defines set-like operations.

    This class expands on the functionality of TimeInterval.
    TimeInterval can only represent sets of time that are contiguous. For some
    applications this is all that is necessary, but for other applications
    (such as those that need to subtract a time interval from another), a
    TimeSet is needed to track non-contiugous sets of time.

    Internally, the TimeSet is just a list of TimeIntervals that exposes the
    same operations as TimeInterval and is largely interoperable.
    """

    def __init__(self, time_intervals: List[TimeInterval]):
        """Inits the TimeSet.

        Args:
            time_intervals (List[TimeInterval]):
                A list of time intervals to create the TimeSet from.
        """
        self.time_intervals = time_intervals

    def is_empty(self) -> bool:
        """Determines if this time interval is empty."""
        pass

    def __add__(self, other: Union[Self, TimeInterval]) -> Self:
        """Implements set addition between this TimeInterval and another TimeInterval or Timeset.

        Args:
            other (Union[Self, TimeSet]):
                The other object. Either a TimeInterval or a TimeSet.
        """
        pass

    def __sub__(self, other: Union[Self, TimeInterval]) -> Self:
        """Implements set subtraction between this TimeInterval and another TimeInterval or Timeset.

        Args:
            other (Union[Self, TimeSet]):
                The other object. Either a TimeInterval or a TimeSet.

        Returns:
            A TimeInterval or a TimeSet, depending on the inputs. May result in an empty TimeSet.
        """
        pass

    def compute_union(self) -> Self:
        """Computes the union of this TimeSet's time intervals.

        Returns:
            A TimeSet containing the union of this TimeSet's time intervals.
            The resulting TimeSet will have no overlapping time intervals.
        """
        pass

    def compute_intersection(self) -> Optional[TimeInterval]:
        """Computes the intersection of this TimeSet's time intervals.

        May return None!!!

        Returns:
            A TimeInterval containing only the time which is common to all
            time intervals that are in this TimeSet. If there is no time common
            to all time intervals, it returns None.
        """
        pass
