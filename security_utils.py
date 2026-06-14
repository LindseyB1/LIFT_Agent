SENSITIVE_MARKERS = [
    "api_key",
    "secret",
    "password",
    "token",
    "classified",
    "ssn",
    "social security",
    "private key",
]


def validate_user_input(text):
    """
    Basic input validation to reduce accidental secret or sensitive-data entry.
    This does not replace human review.
    """
    errors = []
    warnings = []

    lowered = str(text or "").lower()

    for marker in SENSITIVE_MARKERS:
        if marker in lowered:
            warnings.append(
                f"Possible sensitive marker detected: {marker}. Review before submitting."
            )

    if not str(text or "").strip():
        errors.append("Input text is required.")

    return errors, warnings
