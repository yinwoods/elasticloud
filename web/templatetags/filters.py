from django import template


register = template.Library()


@register.filter
def priority_text(value):
    if value == 1:
        text = '低'
    elif value == 2:
        text = '中'
    elif value == 3:
        text = '高'
    else:
        text = 'Unknown'
    return text
