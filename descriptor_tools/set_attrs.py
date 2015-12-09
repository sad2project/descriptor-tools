import functools
from .find_descriptors import get_descriptor_from


# --------------------------------
# functions for descriptors to use
# --------------------------------
def mangle_name(name, prefix='', postfix=''):
    return prefix + name + postfix


def NameMangler(prefix='', postfix=''):
    return functools.partial(mangle_name, prefix=prefix, postfix=postfix)


def set_on(instance, attrname, value):
    instance.__dict__[attrname] = value


# ---------------------------------------------------
# functions for classes to use with their descriptors
# ---------------------------------------------------
class Setters:
    @staticmethod
    def attr(instance, attrname, value, **_):
        setattr(instance, attrname, value)

    @staticmethod
    def basic(instance, attrname, value, *, binding=None):
        desc = get_descriptor_from(instance, attrname, binding=binding)
        desc.__set__(instance, value)

    @staticmethod
    def forced(instance, attrname, value, *, binding=None):
        desc = get_descriptor_from(instance, attrname, binding=binding)
        desc.__set__(instance, value, force=True)

    @staticmethod
    def secret(instance, attrname, value, *, secret='set', binding=None):
        desc = get_descriptor_from(instance, attrname, binding=binding)
        getattr(desc, secret)(instance, value)


def setattribute(
        instance, attrname, value, *, binding=False,
        setters=(Setters.attr, Setters.basic, Setters.forced, Setters.secret)):

    for setter in setters:
        try:
            setter(instance, attrname, value, binding=binding)
            return
        except (TypeError, AttributeError):
            continue
    raise AttributeError("Cannot set attribute '{attrname}' on attr of type"
                         "'{type(attr)}'")


class AttributeSetter:
    def __init__(self, instance, attributes=None):
        self.instance = instance
        self.attributes = {}
        if attributes is not None:
            self.attributes.update(attributes)

    def register(self, attrname, setter, *, binding=False):
        self.attributes[attrname] = (setter, binding)

    def set(self, attrname, value, *, binding=None):
        if attrname in self.attributes:
            self._set_registered(attrname, value)
        else:
            setattribute(self.instance, attrname, value, binding=binding)

    def _set_registered(self, attrname, value):
        strategy = self.attributes[attrname]
        setattribute(self.instance, attrname, value, binding=strategy[1],
                     setters=(strategy[0],))

    def __setattr__(self, attrname, value):
        self.set(attrname, value)
