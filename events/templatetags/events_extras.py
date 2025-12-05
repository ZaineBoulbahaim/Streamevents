from django import template

register = template.Library()

@register.filter
def get_choice_display(value, choices):
    """
    Devuelve el display name de una choice dado su value.
    USO en template: {{ value|get_choice_display:choices }}
    """
    if not value:
        return ""
    
    # Convertir lista de tuplas a diccionario
    try:
        choices_dict = dict(choices)
        return choices_dict.get(value, value)
    except (TypeError, ValueError):
        return value