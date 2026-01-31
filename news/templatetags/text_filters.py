# news/templatetags/text_filters.py
from django import template
from django.utils.html import strip_tags
import html

register = template.Library()


@register.filter
def preview_text(value):
    """
    Turns stored HTML/content into a clean preview:
    - decodes HTML entities (&nbsp; &ldquo; etc.)
    - strips HTML tags
    - normalises whitespace
    """
    if not value:
        return ""

    # Decode entities first
    text = html.unescape(str(value))

    # Strip any tags that still exist
    text = strip_tags(text)

    # Normalise non-breaking spaces and whitespace
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    text = " ".join(text.split())

    return text
