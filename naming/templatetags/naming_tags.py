from django import template

register = template.Library()


@register.filter
def get_field(vocab_dict, field_name):
    """Look up a field in the vocabulary dict."""
    return vocab_dict.get(field_name, {})
