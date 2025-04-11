"""Tests the TimeInterval class."""

from datetime import datetime, timedelta
import pytest
from timeintervals import TimeInterval


def test_normal_construction():
    start: datetime = datetime.now() - timedelta(minutes=1)
    end: datetime = datetime.now()
    
    # test positional and keyword arguments because of pydantic.
    TimeInterval(start=start, end=end)
    TimeInterval(start, end)
