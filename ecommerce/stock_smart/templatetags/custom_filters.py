from django import template

register = template.Library()

@register.filter
def price_format(value):
    try:
        return "{:,.0f}".format(float(value)).replace(',', '.')
    except (ValueError, TypeError):
        return value