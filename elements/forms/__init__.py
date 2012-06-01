form_registry = {}


def is_form_registered(name):
    return name in form_registry


def register_form(name, callback):
    if name in form_registry:
        raise Exception('form %s already registered' % name)

    form_registry[name] = callback


def handle_form(name, request, context, formname):
    if name in form_registry:
        return form_registry[name](request, context, formname)
    else:
        return None
