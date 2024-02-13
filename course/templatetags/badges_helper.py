from django import template

register = template.Library()

@register.filter
def to_stroke_dashoffset(value):
    return int(402 * (1 - value))

@register.filter(name='range') 
def get_range(number):
    return range(number)