from django import template

register = template.Library()


@register.filter
def get_item(diccionario, clave):
    if isinstance(diccionario, dict):
        return diccionario.get(clave, '')
    return ''
