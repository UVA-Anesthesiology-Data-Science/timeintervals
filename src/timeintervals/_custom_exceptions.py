"""Contains custom exceptions for more informative errors."""


class InvalidTimeIntervalError(ValueError):
    pass


class TimeFormatMismatchError(ValueError):
    pass


class UnconvertedDataError(ValueError):
    pass
