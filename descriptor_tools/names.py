from descriptor_tools import get_descriptor


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


def id_name_of(descriptor):
    """
    Returns a string of the hexidecimal version of *descriptor*'s id,
    sans the leading '0'. So, it'll be something like 'xf8e8aa97'
    :param descriptor: descriptor to generate the name for/from
    :return: a generated name for the given descriptor
    """
    return hex(id(descriptor))[1:]