from django import template
from django.forms import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    # Check if the value is a BoundField (a Django form field)
    if isinstance(value, BoundField):
        # Render the field as a widget, adding the new class
        # Ensure that existing classes are preserved if any
        existing_classes = value.field.widget.attrs.get('class', '')
        new_class_attr = f"{existing_classes} {css_class}".strip()
        return value.as_widget(attrs={'class': new_class_attr})
    elif isinstance(value, str):
        # If it's already an HTML string (e.g., from choice.tag),
        # parse it and add the class. This is a more complex scenario.
        # For simplicity and robustness, it's often better to avoid
        # applying `add_class` directly to `choice.tag`.
        # However, if absolutely necessary, you'd need a more robust
        # HTML parser here. For now, let's assume direct string modification
        # for a simple case, or recommend avoiding this for choice.tag.
        
        # This is a very basic and fragile way to add class to an existing HTML string.
        # It assumes the input tag is straightforward.
        # A better approach for choice.tag is to modify the widget's attrs
        # before it's rendered to a string.
        if 'class="' in value:
            return value.replace('class="', f'class="{css_class} ', 1)
        elif '<input' in value: # Basic check for input tag without class
            return value.replace('<input', f'<input class="{css_class}"', 1)
        return value # Fallback if no easy modification
    return value