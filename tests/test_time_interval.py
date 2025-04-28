"""Tests the TimeInterval class."""

from datetime import datetime, timedelta
from pydantic_core._pydantic_core import ValidationError
import pytest
from timeintervals import (
    TimeFormatMismatchError,
    TimeInterval,
    UnconvertedDataError,
)


ONE_MINUTE: timedelta = timedelta(minutes=1)
NOW: datetime = datetime.now()


def test_normal_construction():
    """Tests construction with valid data in the way users would expect to construct objects."""
    start: datetime = NOW - ONE_MINUTE
    end: datetime = NOW

    # Test both positional and keyword argument construction because of pydantic.
    TimeInterval(start=start, end=end)
    TimeInterval(start, end)


def test_end_before_start():
    """Tests that construction raises an exception when end is before start."""
    start: datetime = NOW
    end: datetime = NOW - ONE_MINUTE

    with pytest.raises(ValidationError, match="is greater than"):
        TimeInterval(start, end)


def test_too_many_positional_arguments():
    """Tests construction with too many positional arguments."""
    start: datetime = NOW
    end: datetime = NOW - ONE_MINUTE

    with pytest.raises(TypeError, match="Expected 2 positional arguments"):
        TimeInterval(start, end, "start")


def test_from_strings_valid_data():
    """Tests the from_strings method when it is given valid, properly formatted data."""
    start_str: str = "1732/02/22 16:30"
    end_str: str = "1799/12/14 5:22"
    format_str: str = "%Y/%m/%d %H:%M"

    true_start: datetime = datetime(year=1732, month=2, day=22, hour=16, minute=30)
    true_end: datetime = datetime(year=1799, month=12, day=14, hour=5, minute=22)

    correct_time_interval: TimeInterval = TimeInterval(true_start, true_end)
    created_time_interval: TimeInterval = TimeInterval.from_strings(
        start_str, end_str, format_str
    )
    assert created_time_interval == correct_time_interval


def test_from_strings_format_mismatch():
    """Tests the from_strings method when it is given strings that don't match the given format."""
    start_str: str = "1732/02/22 16:30"
    end_str: str = "1799/12/14 5:22"
    format_str: str = "%Y-%m-%d %H:%M"

    with pytest.raises(TimeFormatMismatchError):
        TimeInterval.from_strings(start_str, end_str, format_str)


def test_from_strings_unconverted_data():
    """Tests the from_strings method with strings containing data than the format can convert."""
    start_str: str = "1732/02/22 16:30:55"
    end_str: str = "1799/12/14 5:22:21"
    format_str: str = "%Y/%m/%d %H:%M"

    with pytest.raises(UnconvertedDataError):
        TimeInterval.from_strings(start_str, end_str, format_str)


def test_from_strings_bad_formatting_string_bad_directive():
    """Tests the from_string method with a bad formatting string due to a bad %(letter)."""
    start_str: str = "1732/02/22 16:30:55"
    end_str: str = "1799/12/14 5:22:21"
    format_str: str = "%Y/%m/%D %H:%M"

    with pytest.raises(ValueError, match="bad directive"):
        TimeInterval.from_strings(start_str, end_str, format_str)


def test_time_elapsed():
    """Tests the time_elapsed method."""
    start: datetime = NOW - ONE_MINUTE
    end: datetime = NOW

    interval: TimeInterval = TimeInterval(start, end)
    assert interval.time_elapsed() == ONE_MINUTE


def test_is_nested_in_fully_nested():
    """Tests the is_nested_in method where one TimeInterval is nested and doesn't share bounds."""
    inner_start: datetime = NOW - ONE_MINUTE
    inner_end: datetime = NOW
    outer_start: datetime = NOW - 2 * ONE_MINUTE
    outer_end: datetime = NOW + ONE_MINUTE

    inner_time_interval: TimeInterval = TimeInterval(inner_start, inner_end)
    outer_time_interval: TimeInterval = TimeInterval(outer_start, outer_end)

    assert inner_time_interval.is_nested_in(outer_time_interval)
    assert not outer_time_interval.is_nested_in(inner_time_interval)


def test_is_nested_in_with_equal_starts():
    """Tests the is_nested_in method where the TimeIntervals have the same start times."""
    start: datetime = NOW - ONE_MINUTE
    inner_end: datetime = NOW
    outer_end: datetime = NOW + ONE_MINUTE

    inner_time_interval: TimeInterval = TimeInterval(start, inner_end)
    outer_time_interval: TimeInterval = TimeInterval(start, outer_end)

    assert inner_time_interval.is_nested_in(outer_time_interval)
    assert not outer_time_interval.is_nested_in(inner_time_interval)


def test_is_nested_in_with_equal_ends():
    """Tests the is_nested_in method where the TimeIntervals have the same end times."""
    inner_start: datetime = NOW - ONE_MINUTE
    outer_start: datetime = NOW - 2 * ONE_MINUTE
    end: datetime = NOW

    inner_time_interval: TimeInterval = TimeInterval(inner_start, end)
    outer_time_interval: TimeInterval = TimeInterval(outer_start, end)

    assert inner_time_interval.is_nested_in(outer_time_interval)
    assert not outer_time_interval.is_nested_in(inner_time_interval)


def test_is_nested_in_equal():
    """Tests the is_nested_in method where the TimeIntervals are equal."""
    start: datetime = NOW - ONE_MINUTE
    end: datetime = NOW

    inner_time_interval: TimeInterval = TimeInterval(start, end)
    outer_time_interval: TimeInterval = TimeInterval(start, end)

    assert inner_time_interval.is_nested_in(outer_time_interval)
    assert outer_time_interval.is_nested_in(inner_time_interval)


def test_is_nested_in_overlapping():
    """Tests the is_nested_in method where the TimeIntervals are overlapping, but not nested."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW
    right_start: datetime = NOW - ONE_MINUTE
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert not left_time_interval.is_nested_in(right_time_interval)
    assert not right_time_interval.is_nested_in(left_time_interval)


def test_is_nested_in_left_end_equals_right_start():
    """Tests the is_nested_in method where the left TimeInterval's end equals the right's start."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW
    right_start: datetime = NOW
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert not left_time_interval.is_nested_in(right_time_interval)
    assert not right_time_interval.is_nested_in(left_time_interval)


def test_is_nested_in_totally_disjoint():
    """Tests the is_nested_in method where the TimeIntervals have a gap between them."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW - ONE_MINUTE
    right_start: datetime = NOW
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert not left_time_interval.is_nested_in(right_time_interval)
    assert not right_time_interval.is_nested_in(left_time_interval)


def test_is_disjoint_with_fully_nested():
    """Tests the is_disjoint_with method where one TimeInterval is nested within the other."""
    inner_start: datetime = NOW - ONE_MINUTE
    inner_end: datetime = NOW
    outer_start: datetime = NOW - 2 * ONE_MINUTE
    outer_end: datetime = NOW + ONE_MINUTE

    inner_time_interval: TimeInterval = TimeInterval(inner_start, inner_end)
    outer_time_interval: TimeInterval = TimeInterval(outer_start, outer_end)

    assert not inner_time_interval.is_disjoint_with(outer_time_interval)
    assert not outer_time_interval.is_disjoint_with(inner_time_interval)


def test_is_disjoint_with_equal_starts():
    """Tests the is_disjoint_with method where the TimeIntervals have the same start times."""
    start: datetime = NOW - ONE_MINUTE
    inner_end: datetime = NOW
    outer_end: datetime = NOW + ONE_MINUTE

    inner_time_interval: TimeInterval = TimeInterval(start, inner_end)
    outer_time_interval: TimeInterval = TimeInterval(start, outer_end)

    assert not inner_time_interval.is_disjoint_with(outer_time_interval)
    assert not outer_time_interval.is_disjoint_with(inner_time_interval)


def test_is_disjoint_with_with_equal_ends():
    """Tests the is_disjoint_with method where the TimeIntervals have the same end times."""
    inner_start: datetime = NOW - ONE_MINUTE
    outer_start: datetime = NOW - 2 * ONE_MINUTE
    end: datetime = NOW

    inner_time_interval: TimeInterval = TimeInterval(inner_start, end)
    outer_time_interval: TimeInterval = TimeInterval(outer_start, end)

    assert not inner_time_interval.is_disjoint_with(outer_time_interval)
    assert not outer_time_interval.is_disjoint_with(inner_time_interval)


def test_is_disjoint_where_intervals_are_equal():
    """Tests the is_disjoint_with method where the TimeIntervals are equal."""
    start: datetime = NOW - ONE_MINUTE
    end: datetime = NOW

    inner_time_interval: TimeInterval = TimeInterval(start, end)
    outer_time_interval: TimeInterval = TimeInterval(start, end)

    assert not inner_time_interval.is_disjoint_with(outer_time_interval)
    assert not outer_time_interval.is_disjoint_with(inner_time_interval)


def test_is_disjoint_with_overlapping_intervals():
    """Tests the is_disjoint_with method where the TimeIntervals are overlapping, but not nested."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW
    right_start: datetime = NOW - ONE_MINUTE
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert not left_time_interval.is_disjoint_with(right_time_interval)
    assert not right_time_interval.is_disjoint_with(left_time_interval)


def test_is_disjoint_with_left_end_equals_right_start():
    """Tests the is_disjoint_with method where the left TimeInterval's end equals the right's start."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW
    right_start: datetime = NOW
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert left_time_interval.is_disjoint_with(right_time_interval)
    assert right_time_interval.is_disjoint_with(left_time_interval)


def test_is_disjoint_with_totally_disjoint():
    """Tests the is_disjoint_with method where the TimeIntervals have a gap between them."""
    left_start: datetime = NOW - 2 * ONE_MINUTE
    left_end: datetime = NOW - ONE_MINUTE
    right_start: datetime = NOW
    right_end: datetime = NOW + ONE_MINUTE

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert left_time_interval.is_disjoint_with(right_time_interval)
    assert right_time_interval.is_disjoint_with(left_time_interval)


def test_eq():
    """Tests the __eq__ method between two TimeIntervals."""
    left_start: datetime = NOW - ONE_MINUTE
    left_end: datetime = NOW
    right_start: datetime = NOW - ONE_MINUTE
    right_end: datetime = NOW

    left_time_interval: TimeInterval = TimeInterval(left_start, left_end)
    right_time_interval: TimeInterval = TimeInterval(right_start, right_end)

    assert left_time_interval == right_time_interval
