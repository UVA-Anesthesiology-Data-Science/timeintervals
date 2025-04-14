"""Tests the TimeSet class."""

import pytest
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
    minuend: TimeInterval = TimeInterval(NOW - 2*ONE_MINUTE, NOW - ONE_MINUTE)
    subtrahend: TimeInterval = TimeInterval(NOW, NOW + ONE_MINUTE)

    diff: TimeSet = TimeSet._subtract_timeinterval_from_timeinterval(minuend, subtrahend)
    assert diff == TimeSet([])

