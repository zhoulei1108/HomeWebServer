from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """
    从字典或类字典对象中取值，避免模板访问不存在键时报错。
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

