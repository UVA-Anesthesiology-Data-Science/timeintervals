"""A module defining the TimeSet class, a set of TimeIntervals."""

from .time_interval import TimeInterval
from typing import List, Optional, Union
from typing_extensions import Self


class TimeSet:
    """A set of TimeIntervals that defines set-like operations.

    This class expands on the functionality of TimeInterval.
    TimeInterval acts as the basic data that TimeSet is built from. For some
    applications this is all that is necessary, but for most applications that
    involve time, doing set arithmetic is necessary. TimeInterval does not
    provide any functionality for set arithmetic on its own, but when added to
    a TimeSet, it does.

    The reason this class is required is due to some set operations breaking the
    continuity of the TimeInterval. For example, assume TimeInterval B is
    totally nested in TimeInterval A. Then, A - B is a valid set operation, but
    the result of this is two TimeIntervals, one from the start of A to the
    start of B, and one from the end of B to the end of A. If A and B are
    equal, then the result is an empty TimeInterval, or None. Thus, a method on
    TimeInterval that implements set subtraction could return three types. By
    wrapping TimeInterval in TimeSet, we can guarantee that it will always
    return a TimeSet, and the user can carefully implement the unwrapping of
    the TimeSet in only on eplace.
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
