class TextFormatter:
    """Utility for formatting text strings."""

    def capitalize_words(self, text):
        """Capitalize the first letter of each word."""
        return " ".join(word.capitalize() for word in text.split())

    def truncate(self, text, max_len):
        """Truncate text to max_len characters, adding '...' if truncated."""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."  # BUG: should be text[:max_len - 3] + "..."
