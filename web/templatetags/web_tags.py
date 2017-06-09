from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_settings(name):
    return getattr(settings, name, "")


@register.filter
def priority_text(value):
    text = "UnKnown"
    if value == 1:
        text = "Low"
    elif value == 2:
        text = "Medium"
    elif value == 3:
        text = "High"
    return text
