"""A module defining the TimeInterval class, a construct for working with intervals of time."""

from datetime import datetime, timedelta
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class TimeInterval(BaseModel):
    """The TimeInterval class represents a set of time between a start and an end.
    
    TimeIntervals are immutable by default, any operation on them results in a new TimeInterval.
    """

    start: datetime = Field(frozen=True)
    end: datetime = Field(frozen=True)

    @model_validator(mode="after")
    def check_end_gt_start(self) -> Self:
        """Checks to make sure end is greater than start."""
        if self.end < self.start:
            raise ValueError(
                f"Cannot construct TimeInterval: {self.end} is greater than {self.start}."
            )
        return self

    def __init__(self, *args, **kwargs):
        """An override of pydantic's __init__ function to allow for positional arguments.

        Without this override, the constructor TimeInterval(start=start, end=end) would work,
        but the constructor TimeInterval(start, end) would fail. Users of this package expect
        to be able to use both.
        """
        if args:
            if len(args) != 2:
                raise TypeError(f"Expected 2 positional arguments, got {len(args)}")
            kwargs["start"] = args[0]
            kwargs["end"] = args[1]
        super().__init__(**kwargs)

    def time_elapsed(self) -> timedelta:
        """The amount of time between this TimeInterval's start and end.
        
        Returns:
            A timedelta containing the amount of time between start and end.
        """
        return self.end - self.start
