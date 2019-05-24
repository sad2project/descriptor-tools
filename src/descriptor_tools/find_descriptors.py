import inspect

__author__ = 'Jake'
__all__ = ['get_descriptor', 'get_descriptor_from']


def get_descriptor(cls, descname):
    """
    Returns the descriptor object that is stored under *descname* instead of
    whatever the descriptor would have returned from its `__get__()` method.
    :param cls: class to find the descriptor on
    :param descname: name of the descriptor
    :return: the descriptor stored under *descname* on *instance*
    """
    return inspect.getattr_static(cls, descname)


def get_descriptor_from(instance, descname):
    """
    Returns the descriptor object that is stored under *descname* instead of
    whatever the descriptor would have returned from its `__get__()` method.
    :param instance: instance to find the descriptor on
    :param descname: name of the descriptor
    :return: the descriptor stored under *descname* on *instance*
    """
    return get_descriptor(type(instance), descname)
