from django import template

register = template.Library()

@register.filter
def range_filter(value):
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def subtract(value, arg):
    try:
        return range(int(value) - int(arg))
    except (ValueError, TypeError):
        return range(0)