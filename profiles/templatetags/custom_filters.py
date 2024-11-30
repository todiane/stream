from django import template

register = template.Library()

@register.filter
def remove_linebreaks(value):
    return value.replace("\n", " ").replace("&nbsp;", " ")
