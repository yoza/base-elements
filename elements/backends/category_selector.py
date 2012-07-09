from django.conf import settings
from django.utils.safestring import mark_safe


def category_options(children, category):
    children = sorted(list(children.filter(status=settings.OBJECT_PUBLISHED)), key=lambda p: p.name.lower())
    for child in children:
        sclass = sel = ""
        if category == child.slug:
            sel = 'selected=selected'
            sclass = 'selected'
        disabled = ""
        if child.check_empty():
            disabled = 'disabled = "disabled"'
        indent = ""
        for i in range(child.get_level()):
            indent += '&nbsp;&nbsp;&nbsp;&nbsp;'

        options = mark_safe(u'<option %s class="%s level_%s" value=%s %s>%s%s</option>' % (sel, sclass, child.get_level(), child.slug, disabled, mark_safe(indent), child.name.strip()))
        if child.get_children():
            for option in category_options(child.get_children(), category):
                options += option
        yield options


def get_listcategories(categories, category, zero_name):
    sel = ""
    if category in 'all':
        sel = 'selected="selected"'
    options = u'<option %s value=all>%s</option>' % (sel, zero_name)
    for option in category_options(categories, category):
        options += option

    return  options




