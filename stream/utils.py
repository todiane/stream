from django.utils.text import slugify as django_slugify
import re


def custom_slugify(text):
    """
    Custom slugify function that preserves apostrophes for English language content
    but still creates valid URLs
    """
    # Replace smart/curly quotes with straight quotes
    text = text.replace(""", "'").replace(""", "'").replace('"', '"').replace('"', '"')

    # Preserve apostrophes in words like "Shakespeare's" but remove other special characters
    text = re.sub(
        r"([a-zA-Z])'([a-zA-Z])", r"\1-\2", text
    )  # Replace apostrophes in words with hyphens
    text = django_slugify(text)  # Handle all other characters

    return text
