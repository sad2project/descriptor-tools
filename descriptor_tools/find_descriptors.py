import sys
import inspect


__all__ = ['get_descriptor', 'get_descriptor_from']


major, minor, _, __, ___ = sys.version_info
is3_2plus = (major == 3 and minor >= 2) or major > 3


def get_descriptor(cls, descname, *, binding=None):
    """
    Returns the descriptor object that is stored under *descname* instead of
    whatever the descriptor would have returned from its `__get__()` method.
    :param cls: class to find the descriptor on
    :param descname: name of the descriptor
    :param binding: *optional* - whether or not the descriptor is a binding
    descriptor. If left unspecified, the function may determine it for itself.
    This parameter is useless with Python 3.2 and above, as it uses the
    `inspect` module's `getattr_static()` instead.
    :return: the descriptor stored under *descname* on *instance*
    """
    if is3_2plus:
        return inspect.getattr_static(cls, descname)
    elif binding is None:
        return _unknown_binding_descriptor(cls, descname)
    else:
        return _known_binding_descriptor(cls, descname, binding)


def get_descriptor_from(instance, descname, *, binding=None):
    """
    Returns the descriptor object that is stored under *descname* instead of
    whatever the descriptor would have returned from its `__get__()` method.
    :param instance: instance to find the descriptor on
    :param descname: name of the descriptor
    :param binding: *optional* - whether or not the descriptor is a binding
    descriptor. If left unspecified, the function may determine it for itself.
    This parameter is useless with Python 3.2 and above, as this uses the
    inspect module's `getattr_static()` instead.
    :return: the descriptor stored under *descname* on *instance*
    """
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


