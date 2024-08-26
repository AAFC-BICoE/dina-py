from marshmallow import ValidationError

def ValidateEnums(enum_class):
    """Validates a string against an enum.

    Args:
        enum_class: The enum class to validate against.

    Returns:
        The validated value or raises a ValidationError.
    """
    def validate(value):
        if value not in enum_class.__members__.keys():
            raise ValidationError(f"Invalid value '{value}'. Must be one of: {enum_class.__members__.keys()}")
        return value

    return validate
