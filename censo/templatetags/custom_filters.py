from django import template
from censo.models import JefeFamiliar

register = template.Library()

@register.filter(name='is_jefe_familiar')
def is_jefe_familiar(value):
    return isinstance(value, JefeFamiliar)