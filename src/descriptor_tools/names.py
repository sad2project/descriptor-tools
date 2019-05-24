# coding=utf-8
from descriptor_tools import get_descriptor


__author__ = 'Jake'
__all__ = ['name_of', 'id_name_of']


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
    name = _first(attr for attr in dir(owner)
                  if (get_descriptor(owner, attr) is descriptor))
    if name is None:
        raise RuntimeError(
            str.format(
                "The descriptor, '{}', does not exist on type, '{}'",
                descriptor,
                owner.__qualname__))
    return name


def _first(iter):
    return next(iter, None)


def id_name_of(descriptor):
    """
    Returns a string of the hexidecimal version of *descriptor*'s id,
    sans the leading '0'. So, it'll be something like 'xf8e8aa97'. It
    removes the 0 so that it will start with an alpha character,
    allowing it to still be a proper Python identifier, which keeps it
    from breaking `dir()`
    
    :param descriptor: descriptor to generate the name for/from
    :return: a generated name for the given descriptor
    """
    return hex(id(descriptor))[1:]
