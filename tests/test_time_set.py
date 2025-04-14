"""Tests the TimeSet class."""

import pytest
from datetime import datetime, timedelta
from timeintervals import (
    TimeFormatMismatchError,
    TimeInterval,
    TimeSet,
    UnconvertedDataError,
)

ONE_MINUTE: timedelta = timedelta(minutes=1)

def test_is_empty():
    """Tests the is_empty method."""
    now: datetime = datetime.now()
    empty_time_set: TimeSet = TimeSet([])
    non_empty_time_set: TimeSet = TimeSet([TimeInterval(now - ONE_MINUTE, now)])
    assert empty_time_set.is_empty()
    assert not non_empty_time_set.is_empty()
