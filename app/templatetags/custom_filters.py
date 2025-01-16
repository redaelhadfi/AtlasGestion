from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def clp(value):
    try:
        return f"${value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value
