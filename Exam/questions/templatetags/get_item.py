from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def get_item_option(question, letter):
    return getattr(question, f'option{letter}', '')

@register.filter
def get_option(item, letter):
    return item.get(f"option{letter}", "") 