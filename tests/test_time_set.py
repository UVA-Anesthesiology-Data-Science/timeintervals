"""Tests the TimeSet class."""

from datetime import datetime, timedelta
from timeintervals import TimeInterval, TimeSet


ONE_MINUTE: timedelta = timedelta(minutes=1)
NOW: datetime = datetime.now()


def test_is_empty():
    """Tests the is_empty method."""
    empty_time_set: TimeSet = TimeSet([])
    non_empty_time_set: TimeSet = TimeSet([TimeInterval(NOW - ONE_MINUTE, NOW)])
    assert empty_time_set.is_empty()
    assert not non_empty_time_set.is_empty()


def test_add_time_interval_to_time_set():
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


def test_add_time_set_to_time_set():
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
    pass


def test_sub_timeset_from_timeset_equal():
    """Tests the _subtract_timeset_from_timeset method where the minuend and subtrahend are equal."""
    pass


def test_sub_timeset_from_timeset_some_overlap():
    """Tests the _subtract_timeset_from_timeset method where there is some overlap."""
    pass


def test_sub_empty_timeset_from_timeset():
    """Tests the _subtract_timeset_from_timeset method where the subtrahend is an empty TimeSet."""
    pass


def test_sub_timeset_from_empty_timeset():
    """Tests the _subtract_timeset_from_timeset method where the minuend is an empty TimeSet."""
    pass
