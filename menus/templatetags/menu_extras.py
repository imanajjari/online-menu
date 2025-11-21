from django import template


register = template.Library()


def _normalize_key(key):
    return key


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key) or dictionary.get(str(key))
    return None


@register.filter
def note_text(dictionary, key):
    entry = get_item(dictionary, key)
    if isinstance(entry, dict):
        return entry.get("note", "")
    return ""


@register.filter
def has_note(dictionary, key):
    return bool(get_item(dictionary, key))

