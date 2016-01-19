import sys
import inspect


__all__ = ['get_descriptor', 'get_descriptor_from', 'name_of']


major, minor, _, __, ___ = sys.version_info
is3_2plus = (major == 3 and minor >= 2) or major > 3

if is3_2plus:
    def get_descriptor(cls, descname):
        """
        Returns the descriptor object that is stored under *descname* instead of
        whatever the descriptor would have returned from its `__get__()` method.
        :param cls: class to find the descriptor on
        :param descname: name of the descriptor
        :return: the descriptor stored under *descname* on *instance*
        """
        return inspect.getattr_static(cls, descname)
else:
    def get_descriptor(cls, descname):
        """
        Returns the descriptor object that is stored under *descname* instead of
        whatever the descriptor would have returned from its `__get__()` method.
        :param cls: class to find the descriptor on
        :param descname: name of the descriptor
        :return: the descriptor stored under *descname* on *instance*
        """
        return _find_descriptor(cls, descname)


def get_descriptor_from(instance, descname):
    """
    Returns the descriptor object that is stored under *descname* instead of
    whatever the descriptor would have returned from its `__get__()` method.
    :param instance: instance to find the descriptor on
    :param descname: name of the descriptor
    :return: the descriptor stored under *descname* on *instance*
    """
    return get_descriptor(type(instance), descname)


def _find_descriptor(cls, descname):
    selected_class = _first(clss for clss in cls.__mro__
                            if descname in clss.__dict__)
    return selected_class.__dict__[descname]


def name_of(descriptor, owner):
    """
    Given a descriptor and a class that the descriptor is stored on, returns
    the name of the attribute the descriptor is stored under.
    Also works if the given class is a subclass of the class that *actually*
    has the descriptor attribute
    :param descriptor: descriptor the name is being looked up for
    :param owner: class that "owns" the descriptor
    :return: the name the descriptor is stored under on *owner*
    """
    return _first(attr for attr in dir(owner)
                  if (get_descriptor(owner, attr) is descriptor))


def _first(iter):
    return next(iter, None)
