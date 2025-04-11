"""Tests the TimeInterval class."""

from datetime import datetime, timedelta
from pydantic_core._pydantic_core import ValidationError
import pytest
from timeintervals import TimeInterval


def test_normal_construction():
    start: datetime = datetime.now() - timedelta(minutes=1)
    end: datetime = datetime.now()

    # Test both positional and keyword argument construction because of pydantic.
    TimeInterval(start=start, end=end)
    TimeInterval(start, end)


def test_end_before_start():
    start: datetime = datetime.now()
    end: datetime = datetime.now() - timedelta(minutes=1)

    with pytest.raises(ValidationError, match="is greater than"):
        TimeInterval(start, end)
