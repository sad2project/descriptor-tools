
from . import UnboundAttribute
from descriptor_tools import name_of
from weakref import WeakSet
from functools import wraps


__all__ = ["DescriptorDecorator",
           "Binding",
           "binding",
           "ForcedSet",
           "SecretSet",
           "SetOnce"]


# ******************************************************
# Instance decorators (old-fashioned Design Pattern Way)
# ******************************************************
class DescriptorDecorator:
    def __init__(self, desc):
        self.desc = desc

    def __get__(self, instance, owner):
        if instance is None:
            if hasattr(self.desc, '__get__'):
                return lifted_desc_results(self.desc, self, instance, owner)
            else:
                return self
        else:
            if is_data_desc(self.desc):
                if hasattr(self.desc, '__get__'):
                    return lifted_desc_results(self.desc, self, instance, owner)
            if name_of(self, owner) in instance.__dict__:
                return instance.__dict__[name_of(self, owner)]
            elif hasattr(self.desc, '__get__'):
                return lifted_desc_results(self.desc, self, instance, owner)
            else:
                return self

    def __set__(self, instance, value):
        if is_data_desc(self.desc):
            if hasattr(self.desc, '__set__'):  # delegate if __set__ exists
                self.desc.__set__(instance, value)
            else:  # bad call if it's a data descriptor without __set__
                raise AttributeError('__set__')
        else:  # delegate to instance dictionary
            name = name_of(self, type(instance))
            instance.__dict__[name] = value

    def __delete__(self, instance):
        if hasattr(self.desc, '__delete__'):
            self.desc.__delete__(instance)
        elif is_data_desc(self.desc):
            raise AttributeError('__delete__')
        else:
            try:
                del instance.__dict__[name_of(self, type(instance))]
            except KeyError as e:
                raise AttributeError(e)

    def __getattr__(self, item):
        return getattr(self.desc, item)


def lifted_desc_results(wrapped, wrapper, instance, owner):
    result = wrapped.__get__(instance, owner)
    if result is wrapped:
        return wrapper
    elif isinstance(result, UnboundAttribute):
        return result.lift_descriptor(wrapper)
    else:
        return result


def is_data_desc(desc):
    return hasattr(desc, '__set__') or hasattr(desc, '__delete__')


class Binding(DescriptorDecorator):
    def __get__(self, instance, owner):
        if instance is None:
            return UnboundAttribute(self, owner)
        else:
            return super().__get__(instance, owner)


class SecretSet(DescriptorDecorator):
    def __set__(self, instance, value):
        raise AttributeError("Cannot set a read-only attribute")

    def set(self, instance, value):
        super().__set__(instance, value)


class ForcedSet(DescriptorDecorator):
    def __set__(self, instance, value, force=False):
        if force:
            super().__set__(instance, value)
        else:
            raise AttributeError("Cannot set a read-only attribute")


class SetOnce(DescriptorDecorator):
    def __init__(self, desc):
        super().__init__(desc)
        self.set_instances = WeakSet()

    def __set__(self, instance, value):
        if self._already_set(instance):
            raise AttributeError("Cannot set a read-only attribute")
        else:
            self.set_instances.add(instance)
            super().__set__(instance, value)

    def _already_set(self, instance):
        return instance in self.set_instances


# *****************
# Method decorators
# *****************
def binding(get):
    @wraps(get)
    def __get__(desc, instance, owner):
        if instance is None:
            return UnboundAttribute(desc)
        else:
            return get(desc, instance, owner)
    return __get__