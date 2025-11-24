from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """
    安全地从字典或类字典对象中取值，避免模板中访问不存在的键导致报错。
    """
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        # 支持列表/元组等下标访问
        try:
            return mapping[key]
        except Exception:
            return None
