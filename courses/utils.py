def sanitize_text(text):
    """
    Sanitize text to ensure it's compatible with latin1 encoding.
    Replaces problematic characters with their simple ASCII equivalents.
    """
    if not text:
        return text

    replacements = {
        '"': '"',  # Smart quotes to regular quotes
        '"': '"',
        """: "'",  # Smart apostrophes to regular apostrophes
        """: "'",
        "–": "-",  # En dash to hyphen
        "—": "-",  # Em dash to hyphen
        "…": "...",  # Ellipsis to periods
        "\u2019": "'",  # Another smart apostrophe variant
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Try to encode to latin1 to catch any other problematic characters
    try:
        text.encode("latin1")
    except UnicodeEncodeError:
        # If encoding fails, replace any non-latin1 characters with closest ASCII equivalent
        text = text.encode("ascii", "replace").decode("ascii")

    return text
