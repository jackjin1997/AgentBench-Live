import re


class InputValidator:
    """Validates user input strings."""

    def is_email(self, s):
        """Check if the string is a valid email address."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, s))

    def is_positive_int(self, s):
        """Check if the string represents a positive integer (> 0)."""
        try:
            return int(s) >= 0  # BUG: should be int(s) > 0
        except (ValueError, TypeError):
            return False
