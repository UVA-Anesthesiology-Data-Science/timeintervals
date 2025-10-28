"""Tests the TimeSet class."""

from datetime import datetime, timedelta
import pytest
from timeintervals import TimeInterval, TimeSet
from typing import List, Optional


NOW: datetime = datetime.now()
ONE_MINUTE: timedelta = timedelta(minutes=1)


def test_is_empty():
    """Tests the is_empty method."""
    empty_time_set: TimeSet = TimeSet([])
    non_empty_time_set: TimeSet = TimeSet([TimeInterval(NOW - ONE_MINUTE, NOW)])
    assert empty_time_set.is_empty()
    assert not non_empty_time_set.is_empty()


def test_add_timeinterval_to_timeset():
    """Tests the __add__ method by adding a TimeInterval to a TimeSet."""
    new_time_interval: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)
    pre_add_time_set: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        ]
    )
    post_add_time_set: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW, NOW + ONE_MINUTE),
        ]
    )
    assert (pre_add_time_set + new_time_interval) == post_add_time_set


def test_add_timeset_to_timeset():
    """Tests the __add__ method by adding a TimeInterval to a TimeSet."""
    new_time_set: TimeSet = TimeSet([TimeInterval(NOW, NOW + ONE_MINUTE)])
    pre_add_time_set: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        ]
    )
    post_add_time_set: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW, NOW + ONE_MINUTE),
        ]
    )
    assert (pre_add_time_set + new_time_set) == post_add_time_set


def test_add_non_timeset_non_timeinterval_to_timeset():
    """Tests the __add__ methods ability to throw an error when adding a wrong type to TimeSet."""
    with pytest.raises(ValueError, match="\"other\" is a"):
        new_string: str = "TimeSet([TimeInterval(NOW, NOW + ONE_MINUTE)])"
        pre_add_time_set: TimeSet = TimeSet(
            [
                TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
                TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            ]
        )
        pre_add_time_set + new_string


def test_sub_timeinterval_from_timeinterval_disjoint():
    """Tests the _subtract_timeinterval_from_timeinterval method with disjoint timeintervals."""
    minuend: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    assert diff == TimeSet([TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE)])


def test_sub_timeinterval_from_timeinterval_overlapping_subtrahend_right():
    """Tests the _subtract_timeinterval_from_timeinterval method with overlapping timeintervals.

    These TimeIntervals are constructed such that the minuend is overlapping with the subtrahend
    on the right side (subtrahend.start < minuend.end).
    """
    minuend: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)

    diff_general_method: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    diff_specific_method: TimeSet = TimeSet._subtract_non_nested_timeintervals(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE)])

    assert diff_general_method == true_diff
    assert diff_specific_method == true_diff


def test_sub_timeinterval_from_timeinterval_overlapping_subtrahend_left():
    """Tests the _subtract_timeinterval_from_timeinterval method with overlapping timeintervals.

    These TimeIntervals are constructed such that the minuend is overlapping with the subtrahend
    on the left side (subtrahend.end < minuend.start).
    """
    minuend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)

    diff_general_method: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    diff_specific_method: TimeSet = TimeSet._subtract_non_nested_timeintervals(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([TimeInterval(NOW, NOW + ONE_MINUTE)])

    assert diff_general_method == true_diff
    assert diff_specific_method == true_diff


def test_sub_timeinterval_from_timeinterval_nested_equal_starts_minuend_greater_end():
    """Tests the _subtract_timeinterval_from_timeinterval method with nested timeintervals.

    These TimeIntervals are constructed such that the minuend and subtrahend have the same start,
    but with the minuend having a greater end.
    """
    minuend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)

    diff_general_method: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    diff_specific_method: TimeSet = TimeSet._subtract_nested_timeintervals(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([TimeInterval(NOW, NOW + ONE_MINUTE)])

    assert diff_general_method == true_diff
    assert diff_specific_method == true_diff


def test_sub_timeinterval_from_timeinterval_nested_equal_starts_subtrahend_greater_end():
    """Tests the _subtract_timeinterval_from_timeinterval method with nested timeintervals.

    These TimeIntervals are constructed such that the minuend and subtrahend have the same start,
    but with the minuend having a greater end.
    """
    minuend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([])

    assert diff == true_diff


def test_sub_timeinterval_from_timeinterval_nested_equal_ends_minuend_lesser_start():
    """Tests the _subtract_timeinterval_from_timeinterval method with nested timeintervals.

    These TimeIntervals are constructed such that the minuend and subtrahend have the same end,
    but with the minuend having a lesser start.
    """
    minuend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)

    diff_general_method: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    diff_specific_method: TimeSet = TimeSet._subtract_nested_timeintervals(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([TimeInterval(NOW - ONE_MINUTE, NOW)])

    assert diff_general_method == true_diff
    assert diff_specific_method == true_diff


def test_sub_timeinterval_from_timeinterval_nested_equal_ends_subtrahend_lesser_start():
    """Tests the _subtract_timeinterval_from_timeinterval method with nested timeintervals.

    These TimeIntervals are constructed such that the minuend and subtrahend have the same end,
    but with the subtrahend having a lesser start.
    """
    minuend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet([])

    assert diff == true_diff


def test_sub_timeinterval_from_timeinterval_fully_nested():
    """Tests the _subtract_timeinterval_from_timeinterval method with nested timeintervals.

    These TimeIntervals are constructed such that the subtrahend is nested inside the
    minuend with neither their start nor end being equal to onen another.
    """
    minuend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + 2 * ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)

    diff_general_method: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(
        minuend, subtrahend
    )
    diff_specific_method: TimeSet = TimeSet._subtract_nested_timeintervals(
        minuend, subtrahend
    )
    true_diff: TimeSet = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        ]
    )

    assert diff_general_method == true_diff
    assert diff_specific_method == true_diff


def test_sub_timeinterval_from_timeset_disjoint():
    """Tests the _subtract_timeinterval_from_set method with the subtrahend being disjoint."""
    minuend: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )
    subtrahend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )

    assert diff == true_diff


def test_sub_timeinterval_from_timeset_overlapping_all():
    """Tests the _subtract_timeinterval_from_set method with the subtrahend overlapping all."""
    minuend: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )
    subtrahend: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )

    assert diff == true_diff


def test_sub_timeinterval_from_timeset_some_overlap():
    """Tests the _subtract_timeinterval_from_set method with the subtrahend overlapping some."""
    minuend: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 3 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )

    assert diff == true_diff


def test_sub_timeinterval_from_empty_timeset():
    """Tests the _subtract_timeinterval_from_set method with the minuend being an empty TimeSet."""
    minuend: TimeSet = TimeSet([])
    subtrahend: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet([])

    assert diff == true_diff


def test_sub_timeset_from_timeset_disjoint():
    """Tests the _subtract_timeset_from_timeset method with a disjoint minuend and subtrahend."""
    minuend: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )
    subtrahend: TimeInterval = TimeSet(
        [
            TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        ]
    )

    diff: TimeSet = TimeSet._subtract_timeset_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )

    assert diff == true_diff


def test_sub_timeset_from_timeset_equal():
    """Tests the _subtract_timeset_from_timeset method where the minuend and subtrahend are equal."""
    minuend: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )
    subtrahend: TimeInterval = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )

    diff: TimeSet = TimeSet._subtract_timeset_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet([])

    assert diff == true_diff


def test_sub_timeset_from_timeset_some_overlap():
    """Tests the _subtract_timeset_from_timeset method where there is some overlap."""
    minuend: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )
    subtrahend: TimeInterval = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        ]
    )

    diff: TimeSet = TimeSet._subtract_timeset_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet([TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE)])

    assert diff == true_diff


def test_sub_empty_timeset_from_timeset():
    """Tests the _subtract_timeset_from_timeset method where the subtrahend is an empty TimeSet."""
    minuend: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )
    subtrahend: TimeInterval = TimeSet([])

    diff: TimeSet = TimeSet._subtract_timeset_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )

    assert diff == true_diff


def test_sub_timeset_from_empty_timeset():
    """Tests the _subtract_timeset_from_timeset method where the minuend is an empty TimeSet."""
    minuend: TimeSet = TimeSet([])
    subtrahend: TimeInterval = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )

    diff: TimeSet = TimeSet._subtract_timeset_from_timeset(minuend, subtrahend)

    true_diff: TimeSet = TimeSet([])

    assert diff == true_diff


def test_sub_operator_overloading():
    """Tests whether the __sub__ dunder method is properly overloading the - operator."""
    minuend: TimeSet = TimeSet([])
    time_set_subtrahend: TimeSet = TimeSet(
        [TimeInterval(NOW - 2 * ONE_MINUTE, NOW), TimeInterval(NOW - ONE_MINUTE, NOW)]
    )
    time_interval_subtrahend: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    illegal_subtrahend: float = 4.2
    true_diff: TimeSet = TimeSet([])

    assert minuend - time_set_subtrahend == true_diff
    assert minuend - time_interval_subtrahend == true_diff
    with pytest.raises(ValueError):
        minuend - illegal_subtrahend


def test_union_all_disjoint():
    """Tests the compute_internal_union method with a TimeSet consisting of disjoint TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
        TimeInterval(NOW, NOW + ONE_MINUTE),
        TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
    ]
    unioned_timeset: TimeSet = TimeSet(time_intervals)
    assert TimeSet(time_intervals).compute_internal_union() == unioned_timeset


def test_union_all_disjoint_but_touching():
    """Tests the compute_internal_union method with disjoint but touching TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
    ]
    true_union: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE)
    ]
    unioned_timeset: TimeSet = TimeSet(true_union)

    assert TimeSet(time_intervals).compute_internal_union() == unioned_timeset


def test_union_overlapping_timeintervals():
    """Tests the compute_internal_union method with overlapping, non-nested TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW),
        TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + 3 * ONE_MINUTE, NOW + 4 * ONE_MINUTE),
    ]
    true_union: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + 3 * ONE_MINUTE, NOW + 4 * ONE_MINUTE),
    ]
    unioned_timeset: TimeSet = TimeSet(true_union)
    assert TimeSet(time_intervals).compute_internal_union() == unioned_timeset


def test_union_nested_timeintervals():
    """Tests the compute_internal_union method with nested TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
    ]
    true_union: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
    ]
    unioned_timeset: TimeSet = TimeSet(true_union)
    assert TimeSet(time_intervals).compute_internal_union() == unioned_timeset


def test_union_mixed_timeintervals():
    """Tests the compute_internal_union method with a relatively realistic group of TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        TimeInterval(NOW + 4 * ONE_MINUTE, NOW + 5 * ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW),
        TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
    ]
    true_union: List[TimeInterval] = [
        TimeInterval(NOW - 3 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        TimeInterval(NOW + 4 * ONE_MINUTE, NOW + 5 * ONE_MINUTE),
    ]
    unioned_timeset: TimeSet = TimeSet(true_union)
    assert TimeSet(time_intervals).compute_internal_union() == unioned_timeset


def test_eq_not_equal():
    """Tests the __eq__ method when the TimeSets are not equal."""
    time_intervals_1: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        TimeInterval(NOW + 4 * ONE_MINUTE, NOW + 5 * ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW),
        TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
    ]
    time_intervals_2: List[TimeInterval] = time_intervals_1[1:]
    assert TimeSet(time_intervals_1) != TimeSet(time_intervals_2)


def test_eq_equal():
    """Tests the __eq__ method when the TimeSets are equal."""
    time_intervals_1: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE),
        TimeInterval(NOW + 4 * ONE_MINUTE, NOW + 5 * ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW),
        TimeInterval(NOW - 3 * ONE_MINUTE, NOW - 2 * ONE_MINUTE),
    ]
    time_intervals_2: List[TimeInterval] = sorted(
        time_intervals_1, key=lambda ti: ti.start
    )
    assert TimeSet(time_intervals_1) != TimeSet(time_intervals_2)


def test_compute_internal_intersection_empty_timeset():
    """Tests the compute_internal_intersection method with an empty TimeSet."""
    assert TimeSet([]).compute_internal_intersection().is_empty()


def test_compute_internal_intersection_no_intersection():
    """Tests the compute_internal_intersection method with totally disjoint TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
        TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
    ]
    assert TimeSet(time_intervals).compute_internal_intersection().is_empty()


def test_compute_internal_intersection_touching_boundaries():
    """Tests the compute_internal_intersection method with disjoint but touching TimeIntervals."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
    ]
    assert TimeSet(time_intervals).compute_internal_intersection().is_empty()


def test_compute_internal_intersection_with_one_timeinterval_not_intersecting():
    """Tests the compute_internal_intersection method with one TimeInterval that does not intersect."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW, NOW + 2 * ONE_MINUTE),
        TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE),
    ]
    assert TimeSet(time_intervals).compute_internal_intersection().is_empty()


def test_compute_internal_intersection_with_intersection_present():
    """Tests the compute_internal_intersection method with TimeIntervals that do have an intersection."""
    time_intervals: List[TimeInterval] = [
        TimeInterval(NOW - 2 * ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
        TimeInterval(NOW, NOW + 2 * ONE_MINUTE),
    ]
    true_intersection: TimeSet = TimeSet([TimeInterval(NOW, NOW + ONE_MINUTE)])
    assert TimeSet(time_intervals).compute_internal_intersection() == true_intersection


def test_timeinterval_intersection_timeinterval_1_is_none():
    """Tests the timeinterval_intersection method when time_interval_1 is None."""
    time_interval_1: Optional[TimeInterval] = None
    time_interval_2: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    assert computed_intersection is None


def test_timeinterval_intersection_disjoint_intervals_touching():
    """Tests the timeinterval_intersection method when both intervals are disjoint."""
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    assert computed_intersection is None


def test_timeinterval_intersection_disjoint_intervals_not_touching():
    """Tests the timeinterval_intersection method when both intervals are disjoint."""
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    assert computed_intersection is None


def test_timeinterval_intersection_timeinterval_1_totally_nested_in_timeinterval_2():
    """Tests timeinterval_intersection when timeinterval_1 is nested in timeinterval_2."""
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(
        NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE
    )
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_1_nested_in_timeinterval_2_equal_starts():
    """Tests timeinterval_intersection when time_interval_1 is nested in time_interval_2 and their
    starts are equal.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + 2 * ONE_MINUTE)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_1_nested_in_timeinterval_2_equal_ends():
    """Tests timeinterval_intersection when time_interval_1 is nested in time_interval_2 and their
    ends are equal.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_2_totally_nested_in_timeinterval_1():
    """Tests timeinterval_intersection when time_interval_2 is nested in time_interval_1."""
    time_interval_1: Optional[TimeInterval] = TimeInterval(
        NOW - 2 * ONE_MINUTE, NOW + 2 * ONE_MINUTE
    )
    time_interval_2: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_2_nested_in_timeinterval_1_equal_starts():
    """Tests timeinterval_intersection when time_interval_2 is nested in time_interval_1 and their
    starts are equal.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(
        NOW - ONE_MINUTE, NOW + 2 * ONE_MINUTE
    )
    time_interval_2: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_2_nested_in_timeinterval_1_equal_ends():
    """Tests timeinterval_intersection when time_interval_2 is nested in time_interval_1 and their
    ends are equal.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_1_before_timeinterval_2():
    """Tests the timeinterval_intersection method when there is overlap and timeinterval_1 is
    before timeinterval_2.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    time_interval_2: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_timeinterval_intersection_timeinterval_2_before_timeinterval_1():
    """Tests the timeinterval_intersection method when there is overlap and timeinterval_2 is
    before timeinterval_1.
    """
    time_interval_1: Optional[TimeInterval] = TimeInterval(
        NOW - ONE_MINUTE, NOW + ONE_MINUTE
    )
    time_interval_2: TimeInterval = TimeInterval(NOW - 2 * ONE_MINUTE, NOW)
    computed_intersection: Optional[TimeInterval] = TimeSet._timeinterval_intersection(
        time_interval_1, time_interval_2
    )
    true_intersection: TimeInterval = TimeInterval(NOW - ONE_MINUTE, NOW)
    assert computed_intersection == true_intersection


def test_compute_intersection_equal_timesets():
    """Tests the compute_intersection method when both TimeSets are equal."""
    time_set_1: TimeSet = TimeSet(
        [
            TimeInterval(NOW, NOW + ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    time_set_2: TimeSet = TimeSet(
        [
            TimeInterval(NOW, NOW + ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    true_intersection: TimeSet = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    assert time_set_1.compute_intersection(time_set_2) == true_intersection


def test_compute_intersection_no_overlap():
    """Tests the compute_intersection method when none of the timeintervals overlap."""
    time_set_1: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW)
        ]
    )
    time_set_2: TimeSet = TimeSet(
        [
            TimeInterval(NOW + ONE_MINUTE, NOW + 2 * ONE_MINUTE),
            TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    assert time_set_1.compute_intersection(time_set_2).is_empty()


def test_compute_intersection_with_overlap_1():
    """Tests the compute_intersection method where the TimeSets have overlapping timeintervals."""
    time_set_1: TimeSet = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 4 * ONE_MINUTE)
        ]
    )
    time_set_2: TimeSet = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW + ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    true_intersection: TimeSet = TimeSet(
        [
            TimeInterval(NOW - ONE_MINUTE, NOW),
            TimeInterval(NOW + 2 * ONE_MINUTE, NOW + 3 * ONE_MINUTE)
        ]
    )
    assert time_set_1.compute_intersection(time_set_2) == true_intersection


def test_compute_intersection_with_overlap_2():
    """Tests the compute_intersection method where the TimeSets have overlapping timeintervals."""
    time_set_1: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2 * ONE_MINUTE, NOW + 4 * ONE_MINUTE)
        ]
    )
    time_set_2: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2 * ONE_MINUTE, NOW - ONE_MINUTE),
            TimeInterval(NOW - ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW + 3 * ONE_MINUTE, NOW + 5 * ONE_MINUTE)
        ]
    )
    true_intersection: TimeSet = TimeSet(
        [
            TimeInterval(NOW - 2*ONE_MINUTE, NOW + ONE_MINUTE),
            TimeInterval(NOW + 3 * ONE_MINUTE, NOW + 4 * ONE_MINUTE)
        ]
    )
    assert time_set_1.compute_intersection(time_set_2) == true_intersection


def test_clamp_no_inputs():
    """Tests the clamp method where both inputs are None."""
    pass


def test_clamp_new_start():
    """Tests the clamp method where there is a new start and no new end."""
    pass


def test_clamp_new_end():
    """Tests the clamp method where there is a new end and no new start."""
    pass


def test_clamp_new_start_and_new_end():
    """Tests the clamp method where there is a new start and a new end."""
    pass


def test_clamp_no_timeintervals_within_clamp_range():
    """Tests the clamp method where there are no timeintervals that exist after clamping."""
    pass
