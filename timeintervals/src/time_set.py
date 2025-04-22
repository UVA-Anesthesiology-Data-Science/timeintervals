"""A module defining the TimeSet class, a set of TimeIntervals."""

from .time_interval import TimeInterval
from datetime import datetime
from functools import reduce
from operator import add
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

    def __add__(self, other: Union[Self, TimeInterval]) -> Self:
        """Implements set addition between this TimeInterval and another TimeInterval or Timeset.

        Args:
            other (Union[Self, TimeSet]):
                The other object. Either a TimeInterval or a TimeSet.
        """
        if isinstance(other, TimeSet):
            return TimeSet(self.time_intervals + other.time_intervals)
        elif isinstance(other, TimeInterval):
            return TimeSet(self.time_intervals + [other])
        else:
            raise ValueError(
                f"other is a {type(other)}, not a TimeSet or a TimeInterval."
            )

    def __eq__(self, other: Self) -> bool:
        """Determines if this TimeSet is equal to the other by comparing their time_intervals."""
        return self.time_intervals == other.time_intervals

    def __repr__(self) -> str:
        """An unambiguous string representation of this TimeSet."""
        str_time_intervals: str = [ti.__repr__() for ti in self.time_intervals]
        representation: str = f"TimeSet(time_intervals={str_time_intervals})"
        return representation

    def __sub__(self, subtrahend: Union[Self, TimeInterval]) -> Self:
        """Implements set subtraction between this TimeInterval and another TimeInterval or Timeset.

        Args:
            subtrahend (Union[Self, TimeSet]):
                The other object to subtract from this one. Either a TimeInterval or a TimeSet.
                (subtrahend is the right part of any subtraction, the left part is the minuend)

        Returns:
            A TimeInterval or a TimeSet, depending on the inputs. May result in an empty TimeSet.
        """
        if isinstance(subtrahend, TimeSet):
            return TimeSet._subtract_timeset_from_timeset(self, subtrahend)
        elif isinstance(subtrahend, TimeInterval):
            return TimeSet._subtract_timeinterval_from_timeset(self, subtrahend)
        else:
            raise ValueError(f"Cannot subtract type {type(subtrahend)} from a TimeSet.")

    @staticmethod
    def _subtract_timeset_from_timeset(
        minuend: Self,
        subtrahend: Self,
    ) -> Self:
        """Subtracts a TimeSet from a TimeSet.

        This algorithm sorts the input time intervals and checks every loop if the resulting
        difference is empty, or if the rest of the subtrahends are disjoint with the current
        difference, and breaks the inner loop accordingly. This is slower for smaller TimeSets,
        but provides a better efficiency for larger TimeSets.

        Args:
            minuend (TimeSet):
                The TimeInterval being subtracted from.
            subtrahend (TimeSet):
                The TimeInterval being subtracted.

        Returns:
            A TimeSet containing the difference between the minuend and the subtrahend.
        """
        differences: List[TimeSet] = list()
        sorted_minuend_time_intervals = sorted(
            minuend.time_intervals, key=lambda ti: ti.start
        )
        sorted_subtrahend_time_intervals = sorted(
            subtrahend.time_intervals, key=lambda ti: ti.start
        )
        for minuend_time_interval in sorted_minuend_time_intervals:
            diff: TimeSet = TimeSet([minuend_time_interval])
            for subtrahend_time_interval in sorted_subtrahend_time_intervals:
                diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(
                    diff,
                    subtrahend_time_interval,
                )
                latest_end_in_diff: datetime = max(
                    [ti.end for ti in diff.time_intervals],
                    default=None,  # if the default is triggered, then diff is empty.
                )
                if (
                    diff.is_empty()
                    or subtrahend_time_interval.start > latest_end_in_diff
                ):
                    break
            if not diff.is_empty():
                differences += diff.time_intervals
        return TimeSet(differences)

    @staticmethod
    def _subtract_timeinterval_from_timeset(
        minuend: Self,
        subtrahend: TimeInterval,
    ) -> Self:
        """Subtracts a TimeInterval from a TimeSet.

        Args:
            minuend (TimeSet):
                The TimeInterval being subtracted from.
            subtrahend (TimeInterval):
                The TimeInterval being subtracted.

        Returns:
            A TimeSet containing the difference between the minuend and the subtrahend.
        """
        differences: List[TimeSet] = [
            TimeSet._subtract_timeinterval_from_timeinterval(ti, subtrahend)
            for ti in minuend.time_intervals
        ]
        print(f"Differences: {differences}")
        differences: List[TimeSet] = list(
            filter(lambda ts: not ts.is_empty(), differences)
        )
        return reduce(add, differences, TimeSet([]))

    @staticmethod
    def _subtract_timeinterval_from_timeinterval(
        minuend: TimeInterval, subtrahend: TimeInterval
    ) -> Self:
        """Subtracts two TimeIntervals.

        Args:
            minuend (TimeInterval):
                The TimeInterval being subtracted from.
            subtrahend (TimeInterval):
                The TimeInterval being subtracted.

        Returns:
            A TimeSet containing the difference between the minuend and the subtrahend.
        """
        if minuend.is_disjoint_with(subtrahend):
            return TimeSet([minuend])
        elif minuend.is_nested_in(subtrahend):
            return TimeSet([])
        elif subtrahend.is_nested_in(minuend):
            return TimeSet._subtract_nested_timeintervals(minuend, subtrahend)
        else:
            return TimeSet._subtract_non_nested_timeintervals(minuend, subtrahend)

    @staticmethod
    def _subtract_nested_timeintervals(
        minuend: TimeInterval, subtrahend: TimeInterval
    ) -> Self:
        """Subtracts timeintervals where the subtrahend is nested in the minuend.

        Args:
            minuend (TimeInterval):
                The TimeInterval being subtracted from.
            subtrahend (TimeInterval):
                The TimeInterval being subtracted.

        Returns:
            A TimeSet containing the difference between the minuend and the subtrahend.
        """
        if minuend.start == subtrahend.start:
            return TimeSet([TimeInterval(subtrahend.end, minuend.end)])
        elif minuend.end == subtrahend.end:
            return TimeSet([TimeInterval(minuend.start, subtrahend.start)])
        else:
            return TimeSet(
                [
                    TimeInterval(minuend.start, subtrahend.start),
                    TimeInterval(subtrahend.end, minuend.end),
                ]
            )

    @staticmethod
    def _subtract_non_nested_timeintervals(
        minuend: TimeInterval, subtrahend: TimeInterval
    ) -> Self:
        """Subtracts overlapping TimeIntervals that are not nested.

        Args:
            minuend (TimeInterval):
                The TimeInterval being subtracted from.
            subtrahend (TimeInterval):
                The TimeInterval being subtracted.

        Returns:
            A TimeSet containing the difference between the minuend and the subtrahend.
        """
        if minuend.start < subtrahend.start:
            return TimeSet([TimeInterval(minuend.start, subtrahend.start)])
        elif minuend.start > subtrahend.start:
            return TimeSet([TimeInterval(subtrahend.end, minuend.end)])
        else:
            # Shouldn't be possible unless this method is directly invoked on arbitrary inputs.
            raise ValueError(
                "Minuend and subtrahend are nested, but this method only handles non nested cases."
            )

    def is_empty(self) -> bool:
        """Determines if this time interval is empty."""
        return len(self.time_intervals) == 0

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
