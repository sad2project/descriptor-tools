# coding=utf-8
"""
The `decorators` module contains decorators of both stripes (function
decorators and Gang of Four object decorators) for making different types
of descriptors easier to create.

Function decorators are provided to help with designing your own
descriptors, while the object decorators are used to tweak existing
descriptors.

Function decorators that are included are `binding()`, `forced()`, and
`set_once()`. `binding()` wraps the `__get__()` method on the descriptor
to handle the boring details of creating a descriptor with attribute
binding. The other two wrap the `__set__()` method of a descriptor to
take care of the details for creating a "read-only" attribute.

The included object decorators allow you to wrap instances of existing
descriptors in order to use them as if they were descriptors of the
wrapper types.

There are object decorators for all four types of special accessors:
binding, set-once, forced-set, and secret-set.

All of the provided decorators inherit from `DescriptorDecoratorBase`.
Due to the inability to know ahead of time which of the three descriptor
methods will be defined on the wrapped descriptor, each of them end up
implementing the logic to determine what needs to be done, whether the
wrapped descriptor has the needed method and whether it's a data or
non-data descriptor.

I would have liked to dynamically create the non-automatic methods based
on the object that's wrapped, but "magic" methods go straight to the class
for method lookups, so the interpreter would always think that the non-
automatic methods don't exist.
"""
from descriptor_tools import name_of, DescDict
from functools import wraps
from operator import attrgetter

__author__ = 'Jake'
__all__ = ["DescriptorDecoratorBase",
           "Binding",
           "binding",
           "ForcedSet",
           "SecretSet",
           "SetOnce"]


# ******************************************************
# Instance decorators (old-fashioned Design Pattern Way)
# ******************************************************
class DescriptorDecoratorBase:
    """
    DescriptorDecoratorBase is a base class for making decorator classes
    around descriptors. When making a descriptor decorator, inherit from
    this class to do it. Then only override the necessary methods,
    delegating to `super()` for the primary functionality.

    Note: This class overrides `__getattr__()` in order to delegate to
    methods on the wrapped object that this class doesn't handle, but it can't
    do that for dunder methods, which are typically special-cased and must exist
    on the class of the object to work.
    """
    def __init__(self, desc):
        self.desc = desc

    def __call__(self, *args, **kwargs):
        return self.desc(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            if hasattr(self.desc, '__get__'):
                return _lifted_desc_results(self.desc, self, instance, owner)
            else:
                return self
        else:
            if is_data_desc(self.desc):
                if hasattr(self.desc, '__get__'):
                    return _lifted_desc_results(self.desc, self, instance, owner)
            if name_of(self, owner) in instance.__dict__:
                return instance.__dict__[name_of(self, owner)]
            elif hasattr(self.desc, '__get__'):
                return _lifted_desc_results(self.desc, self, instance, owner)
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
        """
        Redirects unknown attribute lookups to the wrapped descriptor
        :param item: attribute being looked up
        """
        return getattr(self.desc, item)

    def __str__(self):
        return str(self.desc)

    def __repr__(self):
        return repr(self.desc)


def _lifted_desc_results(wrapped, wrapper, instance, owner):
    result = wrapped.__get__(instance, owner)
    if result is wrapped:
        return wrapper
    else:
        return result


def is_data_desc(desc):
    return hasattr(desc, '__set__') or hasattr(desc, '__delete__')


class Binding(DescriptorDecoratorBase):
    """
    Turns the wrapped descriptor into a binding descriptor, which returns an
    UnboundAttribute whenever accessed from the containing class instead of
    from an instance.
    """
    def __call__(self, instance):
        return self.__get__(instance, type(instance))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return super().__get__(instance, owner)

    def __str__(self):
        return "Binding " + super().__str__()

    def __repr__(self):
        return "Binding(" + super().__repr__() + ")"


class _ReadOnly(DescriptorDecoratorBase):
    def __delete__(self, instance):
        raise AttributeError("Cannot delete a read-only attribute")


class SecretSet(_ReadOnly):
    """
    Turns the wrapped descriptor into a secret-set descriptor, which requires that
    the descriptor be directly and the "secret" `set()` method be called in
    order to change the value of the represented attribute, allowing it to be
    "read-only" unless set properly.
    """
    def __set__(self, instance, value):
        raise AttributeError("Cannot set a read-only attribute")

    def set(self, instance, value):
        super().__set__(instance, value)

    def __str__(self):
        return "Secret-Set " + super().__str__()

    def __repr__(self):
        return "SecretSet(" + super().__repr__() + ")"


class ForcedSet(_ReadOnly):
    """
    Turns the wrapped descriptor into a forced-set descriptor, which requires
    that the descriptor be directly and the `__set__()` method be called with the
    keyword argument `force=True` in order to change the value of the represented
    attribute, allowing it to be read-only" unless set properly.
    """
    def __set__(self, instance, value, force=False):
        if force:
            super().__set__(instance, value)
        else:
            raise AttributeError("Cannot set a read-only attribute")

    def __str__(self):
        return "Forced-Set " + super().__str__()

    def __repr__(self):
        return "ForcedSet(" + super().__repr__() + ")"


class SetOnce(_ReadOnly):
    """
    Turns the wrapped descriptor into a set-once descriptor, which only
    allows the attribute to be set one time.
    """
    def __init__(self, desc):
        super().__init__(desc)
        self.set_instances = DescDict()

    def __set__(self, instance, value):
        if self._already_set(instance):
            raise AttributeError("Cannot set a read-only attribute")
        else:
            self.set_instances[instance] = True
            super().__set__(instance, value)

    def _already_set(self, instance):
        return instance in self.set_instances

    def __str__(self):
        return "Set-Once " + super().__str__()

    def __repr__(self):
        return "SetOnce(" + super().__repr__() + ")"


# *****************
# Method decorators
# *****************
def binding(get):
    """
    Decorates the `__get__()` method of a descriptor to turn the it into a
    binding descriptor, which returns an unbound attribute whenever
    accessed from the containing class instead of from an instance.
    """
    @wraps(get)
    def __get__(desc, instance, owner=None):
        if instance is None:
            return desc.__get__
        else:
            return get(desc, instance, owner)
    return __get__


def forced(setter):
    """
    Decorates the `__set__()` method of a descriptor to turn it into a
    forced-set descriptor, which requires that the descriptor be directly and
    the `__set__()` method be called with the keyword argument `force=True`
    in order to change the value of the represented attribute, allowing it
    to be read-only" unless set properly.
    """
    @wraps(setter)
    def __set__(desc, instance, value, forced=False):
        if forced:
            return setter(desc, instance, value)
        else:
            raise AttributeError("Cannot set a read-only attribute")
    return __set__


def set_once(setter):
    """
    Decorates the `__set__()` method of a descriptor to turn it into a
    set-once descriptor, which only allows the attribute to be set one time.
    """
    set_instances = DescDict()
    @wraps(setter)
    def __set__(desc, instance, value):
        if instance in set_instances:
            raise AttributeError("Cannot set a read-only attribute")
        else:
            set_instances[instance] = True
            setter(desc, instance, value)
    return __set__



