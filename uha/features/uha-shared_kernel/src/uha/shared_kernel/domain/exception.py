class ValueObjectEnumError(Exception):
    """Exception raised when a value object receives an invalid value."""

    def __str__(self):
        return "Value Object got invalid value."


class BaseMsgException(Exception):
    """Base exception class for application-specific exceptions."""

    error: str = ""
    message: str = ""
    code: int = 500

    def __str__(self):
        return self.message

    @classmethod
    def create(cls, e: Exception) -> "BaseMsgException":
        """Create a BaseMsgException from another exception."""
        model = cls()
        model.error = str(e)
        model.message = getattr(e, "message", str(e))
        model.code = getattr(e, "code", 500)
        return model
