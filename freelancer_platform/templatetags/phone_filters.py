from django import template

register = template.Library()

@register.filter
def whatsapp_number(value):
    """
    Convert phone number into WhatsApp-friendly format.
    Removes all characters except digits.
    """
    if not value:
        return ''
    return ''.join(filter(str.isdigit, str(value)))

