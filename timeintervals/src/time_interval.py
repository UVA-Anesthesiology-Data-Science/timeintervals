"""A module defining the TimeInterval class, a construct for working with intervals of time."""

from ._custom_exceptions import (
    InvalidTimeIntervalError,
    TimeFormatMismatchError,
    UnconvertedDataError,
)
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
            raise InvalidTimeIntervalError(
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

    @classmethod
    def from_strings(cls, start_str: str, end_str: str, time_format: str) -> Self:
        """Creates a time interval by parsing strings.

        Args:
            start (str):
                The start for the TimeInterval.
            end (str):
                The end for the TimeInterval.
            time_format (str):
                The format for the time. See the 1989 C standard for how to format this
                string. This is plugged directly into strptime.

        Returns:
            A TimeInterval with the start and end corresponding to the start_str and
            end_str parsed by time_format.

        Raises:
            ValueError:
                If time_format does not match the format of start_str, or if unconverted
                data remains in the string.
        """
        try:
            start: datetime = datetime.strptime(start_str, time_format)
            end: datetime = datetime.strptime(end_str, time_format)
            return TimeInterval(start, end)
        except ValueError as e:
            error_message: str = str(e)
            if "does not match format" in error_message:
                raise TimeFormatMismatchError(e)
            elif "unconverted data" in str(e):
                raise UnconvertedDataError(e)
            else:
                raise e
        except Exception as e:
            raise e

    def time_elapsed(self) -> timedelta:
        """The amount of time between this TimeInterval's start and end.

        Returns:
            A timedelta containing the amount of time between start and end.
        """
        return self.end - self.start

    def __repr__(self) -> str:
        """An unambiguous string representation of this TimeInterval."""
        return f"TimeInterval(start={self.start}, end={self.end})"

    def __str__(self) -> str:
        """A human readable string representation of this TimeInterval."""
        return repr(self)
