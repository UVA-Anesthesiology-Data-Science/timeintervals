"""Tests the TimeInterval class."""

from datetime import datetime, timedelta
from pydantic_core._pydantic_core import ValidationError
import pytest
from timeintervals import TimeInterval


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


def test_time_elapsed():
    """Tests the time_elapsed method."""
    now: datetime = datetime.now()
    start: datetime = now - ONE_MINUTE
    end: datetime = now

    interval: TimeInterval = TimeInterval(start, end)
    assert(interval.time_elapsed() == ONE_MINUTE)
