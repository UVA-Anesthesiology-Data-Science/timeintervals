"""A module defining the TimeInterval class, a construct for working with intervals of time."""

from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class TimeInterval(BaseModel):
    """The TimeInterval class represents a set of time between a start and an end."""

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
