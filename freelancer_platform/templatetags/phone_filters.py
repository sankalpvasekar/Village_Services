from django import template

register = template.Library()


def _normalize_phone_for_whatsapp(raw: str) -> str:
    if not raw:
        return ""
    digits = ''.join(ch for ch in str(raw) if ch.isdigit())
    # If it already starts with 91, keep; if 10 digits, prepend 91
    if digits.startswith('91'):
        return digits
    if len(digits) == 10:
        return '91' + digits
    return digits


@register.filter(name='whatsapp_number')
def whatsapp_number(value: str) -> str:
    """Convert arbitrary phone text (e.g. '+91 98765 43210') to '919876543210'."""
    return _normalize_phone_for_whatsapp(value)


