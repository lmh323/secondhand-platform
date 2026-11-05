"""Date and time conversion used by model and persistence code."""

from __future__ import annotations

from datetime import datetime

from .errors import ValidationError

USER_DATETIME_FORMAT = "%Y-%m-%d %H:%M"
FILE_DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


def parse_datetime(value: datetime | str, *, field_name: str = "time") -> datetime:
    """Return a naive local datetime from a supported input value."""

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValidationError(f"{field_name} cannot be empty")
        parsed = None
        for date_format in (USER_DATETIME_FORMAT, FILE_DATETIME_FORMAT):
            try:
                parsed = datetime.strptime(text, date_format)
                break
            except ValueError:
                continue
        if parsed is None:
            raise ValidationError(
                f"{field_name} must use YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM"
            )
    else:
        raise ValidationError(f"{field_name} must be a datetime or formatted string")

    if parsed.tzinfo is not None:
        raise ValidationError(f"{field_name} must use Hong Kong local time without a timezone")
    return parsed.replace(second=0, microsecond=0)


def format_file_datetime(value: datetime) -> str:
    """Format a datetime for the versioned .pim representation."""

    return parse_datetime(value).strftime(FILE_DATETIME_FORMAT)
