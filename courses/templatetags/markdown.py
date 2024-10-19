from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter
def markdown_to_html(text):
    return mark_safe(markdown.markdown(text))
