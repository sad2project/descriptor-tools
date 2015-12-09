def get_descriptor(cls, descname, *, binding=None):
    if binding is None:
        return _unknown_binding_descriptor(cls, descname)
    else:
        return _known_binding_descriptor(cls, descname, binding)


def get_descriptor_from(instance, descname, *, binding=None):
    return get_descriptor(type(instance), descname, binding=binding)


def _known_binding_descriptor(cls, descname, binding):
    attr = getattr(cls, descname)
    return attr.descriptor if binding else attr


def _unknown_binding_descriptor(cls, descname):
    attr = getattr(cls, descname)
    try:
        attr = attr.descriptor
    except AttributeError:
        pass
    return attr


