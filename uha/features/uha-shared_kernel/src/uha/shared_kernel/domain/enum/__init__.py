from enum import StrEnum  # noqa: F401


class ApplicationMode(StrEnum):
    """Application running modes."""

    DEVELOPMENT = "DEV"
    PRODUCTION = "PROD"
    TESTING = "TEST"
