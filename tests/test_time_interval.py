"""Tests the TimeInterval class."""

from datetime import datetime, timedelta
from pydantic_core._pydantic_core import ValidationError
import pytest
from timeintervals import (
    InvalidTimeIntervalError,
    TimeFormatMismatchError,
    TimeInterval,
    UnconvertedDataError,
)


ONE_MINUTE: timedelta = timedelta(minutes=1)


def test_normal_construction():
    """Tests construction with valid data in the way users would expect to construct objects."""
    now: datetime = datetime.now()
    start: datetime = now - ONE_MINUTE
    end: datetime = now

    # Test both positional and keyword argument construction because of pydantic.
    TimeInterval(start=start, end=end)
    TimeInterval(start, end)


def test_end_before_start():
    """Tests that construction raises an exception when end is before start."""
    now: datetime = datetime.now()
    start: datetime = now
    end: datetime = now - ONE_MINUTE

    with pytest.raises(ValidationError, match="is greater than"):
        TimeInterval(start, end)


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


def test_time_elapsed():
    """Tests the time_elapsed method."""
    now: datetime = datetime.now()
    start: datetime = now - ONE_MINUTE
    end: datetime = now

    interval: TimeInterval = TimeInterval(start, end)
    assert interval.time_elapsed() == ONE_MINUTE
