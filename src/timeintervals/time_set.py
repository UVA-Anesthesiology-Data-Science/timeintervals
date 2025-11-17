"""A module defining the TimeSet class, a set of TimeIntervals."""

from .time_interval import TimeInterval
from datetime import datetime
from functools import reduce
from operator import add
from pydantic import BaseModel, Field
from typing import List, Optional, Union


class TimeSet(BaseModel):
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
    the TimeSet in only one place.

    Args:
        time_intervals (List[TimeInterval]):
            The time intervals that form this time set.

    Attributes:
        time_intervals (List[TimeInterval]):
            The time intervals that form this time set.
    """

    time_intervals: List[TimeInterval] = Field(frozen=True)

    def __init__(self, *args, **kwargs):
        """An override of pydantic's __init__ function to allow for positional arguments.

        Without this override, the constructor TimeSet(time_intervals=time_intervals) would work,
        but the constructor TimeSet(time_intervals) would fail. Users of this package expect
        to be able to use both.
        """
        if args:
            if len(args) != 1:
                raise TypeError(f"Expected 1 positional argument, got {len(args)}")
            kwargs["time_intervals"] = args[0]
        super().__init__(**kwargs)

    def __add__(self, other: Union["TimeSet", TimeInterval]) -> "TimeSet":
        """Implements set addition between this TimeInterval and another TimeInterval or Timeset.

        Args:
            other (Union[TimeSet, TimeInterval]):
                The other object. Either a TimeInterval or a TimeSet.
        """
        if isinstance(other, TimeSet):
            return TimeSet(self.time_intervals + other.time_intervals)
        elif isinstance(other, TimeInterval):
            return TimeSet(self.time_intervals + [other])
        else:
            raise TypeError(
                f'"other" is a {type(other)}, not a TimeSet or a TimeInterval.'
            )

    def __eq__(self, other: "TimeSet") -> bool:  # type: ignore
        """Determines if this TimeSet is equal to the other by comparing their time_intervals."""
        return self.time_intervals == other.time_intervals

    def __repr__(self) -> str:
        """An unambiguous string representation of this TimeSet."""
        str_time_intervals: List[str] = [ti.__repr__() for ti in self.time_intervals]
        representation: str = f"TimeSet(time_intervals={str_time_intervals})"
        return representation

    def __sub__(self, subtrahend: Union["TimeSet", TimeInterval]) -> "TimeSet":
        """Implements set subtraction between this TimeInterval and another TimeInterval or Timeset.

        Args:
            subtrahend (Union[TimeSet, TimeInterval]):
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
        minuend: "TimeSet",
        subtrahend: "TimeSet",
    ) -> "TimeSet":
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
        differences: List[TimeInterval] = list()
        sorted_minuend_time_intervals: List[TimeInterval] = sorted(
            minuend.time_intervals, key=lambda ti: ti.start
        )
        sorted_subtrahend_time_intervals: List[TimeInterval] = sorted(
            subtrahend.time_intervals, key=lambda ti: ti.start
        )
        for minuend_time_interval in sorted_minuend_time_intervals:
            diff: TimeSet = TimeSet([minuend_time_interval])
            for subtrahend_time_interval in sorted_subtrahend_time_intervals:
                diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(
                    diff,
                    subtrahend_time_interval,
                )
                if diff.is_empty():
                    break
                latest_end_in_diff: Optional[datetime] = max(
                    [ti.end for ti in diff.time_intervals]
                )
                if subtrahend_time_interval.start > latest_end_in_diff:
                    break
            if not diff.is_empty():
                differences += diff.time_intervals
        return TimeSet(differences)

    @staticmethod
    def _subtract_timeinterval_from_timeset(
        minuend: "TimeSet",
        subtrahend: TimeInterval,
    ) -> "TimeSet":
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
        differences: List[TimeSet] = list(
            filter(lambda ts: not ts.is_empty(), differences)
        )
        return reduce(add, differences, TimeSet([]))

    @staticmethod
    def _subtract_timeinterval_from_timeinterval(
        minuend: TimeInterval, subtrahend: TimeInterval
    ) -> "TimeSet":
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
    ) -> "TimeSet":
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
    ) -> "TimeSet":
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

    def compute_internal_union(self) -> "TimeSet":
        """Computes the union of this TimeSet's time intervals.

        Returns:
            A TimeSet containing the union of this TimeSet's time intervals.
            The resulting TimeSet will have no overlapping time intervals.
        """
        if not self.time_intervals:
            return TimeSet([])
        unioned_timeintervals: List[TimeInterval] = list()
        intervals: List[TimeInterval] = sorted(
            self.time_intervals, key=lambda ti: ti.start
        )
        current_start: datetime = intervals[0].start
        current_end: datetime = intervals[0].end

        for interval in intervals:
            if not TimeInterval(current_start, current_end).is_disjoint_with(interval):
                if interval.end > current_end:
                    current_end: datetime = interval.end
            elif interval.start == current_end:
                current_end: datetime = interval.end
            else:
                unioned_timeintervals.append(TimeInterval(current_start, current_end))
                current_start: datetime = interval.start
                current_end: datetime = interval.end
        unioned_timeintervals.append(TimeInterval(current_start, current_end))

        return TimeSet(unioned_timeintervals)

    def compute_internal_intersection(self) -> "TimeSet":
        """Computes the intersection of this TimeSet's time intervals.

        The intersection of a TimeSet can only result in a singlular TimeInterval, or
        an empty TimeInterval. To avoid returning Nones, this method will always return
        a TimeSet. In the event that there is an intersection, it will contain one
        TimeInterval, and in the event that there is no intersection, it will be empty.

        Returns:
            A TimeSet containing only the time which is common to all
            time intervals that are in this TimeSet, which could be none.
        """
        if self.is_empty():
            return TimeSet([])
        intersection: Optional[TimeInterval] = reduce(
            TimeSet._timeinterval_intersection,
            self.time_intervals[1:],
            self.time_intervals[0],
        )
        if intersection is not None:
            return TimeSet([intersection])
        else:
            return TimeSet([])

    @staticmethod
    def _timeinterval_intersection(
        time_interval_1: Optional[TimeInterval], time_interval_2: TimeInterval
    ) -> Optional[TimeInterval]:
        """A helper function for compute_intersection.

        Args:
            time_interval_1 (Optional[TimeInterval]):
                The first TimeInterval. Could be None.
            time_interval_2 (TimeInterval)
                The second TimeInterval.

        Returns:
            A TimeInterval with the time common to both TimeIntervals.
            Returns None if there is no time in common, or if either of the
            TimeIntervals are None.
        """
        if time_interval_1 is None:
            return None
        if time_interval_1.is_disjoint_with(time_interval_2):
            return None
        if time_interval_1.is_nested_in(time_interval_2):
            return time_interval_1
        if time_interval_2.is_nested_in(time_interval_1):
            return time_interval_2
        latest_start: datetime = max(time_interval_1.start, time_interval_2.start)
        earliest_end: datetime = min(time_interval_1.end, time_interval_2.end)
        return TimeInterval(latest_start, earliest_end)

    def compute_intersection(self, other: "TimeSet") -> "TimeSet":
        """Computes the intersection of this TimeSet with the other TimeSet.

        Args:
            other (TimeSet):
                The other TimeSet to intersection with this one.

        Returns:
            The intersection of this TimeSet and the other TimeSet.
        """
        this_timeset_union: TimeSet = self.compute_internal_union()
        other_timeset_union: TimeSet = other.compute_internal_union()

        intersection_intervals: List[TimeInterval] = []
        for this_interval in this_timeset_union.time_intervals:
            for other_interval in other_timeset_union.time_intervals:
                intersection: Optional[TimeInterval] = (
                    TimeSet._timeinterval_intersection(
                        this_interval,
                        other_interval,
                    )
                )
                if intersection is not None:
                    intersection_intervals.append(intersection)

        return TimeSet(intersection_intervals)

    def compute_union(self, other: "TimeSet") -> "TimeSet":
        """Computes the union of this TimeSet with the other TimeSet.

        This method is merely shorthand for combining the time intervals from two TimeSets
        together and computing that TimeSet's union.

        Args:
            other (TimeSet):
                The other TimeSet to union with this one.

        Returns:
            The union of this TimeSet and the other TimeSet.
        """
        return TimeSet(
            self.time_intervals + other.time_intervals
        ).compute_internal_union()

    def clamp(
        self, new_start: Optional[datetime] = None, new_end: Optional[datetime] = None
    ) -> "TimeSet":
        """Clamps the timeintervals in the timeset to a new start, a new end, or both.

        Passing None for new_start or new_end means there is no bound on that side.

        Args:
            new_start (Optional[datetime]):
                The new start to clamp to. If None, start times are unbounded. Defaults to None.
            new_end (Optional[datetime]):
                The new end to clamp to. If None, end times are unbounded. Defaults to None.

        Returns:
             A new TimeSet with the times of all time intervals clamped to the new times
             or removed if the interval is not within the new start and end. If no time
             intervals fit in the clamped range, an empty TimeSet is returned. Allows for empty
             time intervals to exist in the clamped output.
        """
        clamped_intervals: List[TimeInterval] = list()
        for time_interval in self.time_intervals:
            start: datetime = time_interval.start
            end: datetime = time_interval.end

            if new_start is not None and start < new_start:
                start: datetime = new_start
            if new_end is not None and end > new_end:
                end: datetime = new_end

            if end >= start:
                new_interval: TimeInterval = TimeInterval(start, end)
                clamped_intervals.append(new_interval)

        return TimeSet(clamped_intervals)
