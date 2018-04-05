from abc import ABCMeta, abstractmethod

from descriptor_tools import name_of, DescDict
from descriptor_tools.decorators import binding


# Potential replacement for the current Instance Property system that will be even easier to use
# unfinished and untested. Do not use.


class InstanceProperty:
    def __init__(self, deleg_prop_creator):
        self._deleg_prop_creator = deleg_prop_creator
        self._prop_storage = DescDict()
        self._names = {}
        
    def __set_name__(self, owner, name):
        self._names[owner] = name
       
    def _name_for(self, owner):
        try:
            return self._names[owner]
        except KeyError:
            self._names[owner] = name_of(self, owner)
            return self._names[owner]
    
    @binding
    def __get__(self, instance, owner):
        try:
            return self._prop_storage[instance].get()
        except KeyError:
            raise AttributeError(
                "Instance property '{}' not yet initialized".format(
                    self._name_for(owner)))

    def __set__(self, instance, value):
        try:
            property = self._prop_storage[instance]
            property.set(value)
        except KeyError:
            property = self._deleg_prop_creator(
                value,
                self._name_for(type(instance)),
                instance)
            self._prop_storage[instance] = property
        
    def __delete__(self, instance):
        try:
            property = self._prop_storage[instance]
        except KeyError:
            raise AttributeError(self._name_for(type(instance)))

        # in order to NOT delete it, we need the delegated property to have the
        # do_not_delete attribute and have it set to True/truthy
        if not (hasattr(property, "do_not_delete") and property.do_not_delete):
            try:
                property.delete()  # delegated properties can implement a delete() to do any necessary cleanup
            except AttributeError:
                pass
            del self._prop_storage[instance]
        else:
            raise AttributeError(
                "Instance property '{}' cannot be deleted".format(
                    self._name_for(type(instance))))


class DelegatedProperty(metaclass=ABCMeta):
    """
    A Delegated Property is the kind of property you always wanted to write; it
    only knows about and deals with a single instance of the class while
    :InstanceProperty deals with all the details that were always so difficult
    with descriptors.

    It is not required to subclass :DelegatedProperty to create one, but it does
    help label the class for what it is.

    To create a Delegated Property, there at least 2 methods that you need:
    `__init__()`
    `get()`
    If you want the Delegated Property to not be read-only, you will also need
    `set()`.

    Implementing `__init__()`:
    `__init__()` will for sure have 2 parameters, and possibly more. The
    two gauranteed parameters are `instance` and `name`, which will be provided
    as keyword arguments, which can be passed to `super().__init__()`, where
    they will be stored in `_instance` and `_name attributes`. The arguments
    will be the last ones passed in.

    If you're not truly inheriting from `DelegatedProperty`, then be sure to
    save `instance` and `name` in `_instance` and `_name` attributes, since
    some decorator properties take advantage of these.

    In some rare cases, it's possible your Delegated Property will need even
    more parameters in order to be properly initialized. If this is the case,
    simply require them, preferably before the `instance` and `name` parameters.

    Users using your specific Delegated Property are the ones required to
    provide all the arguments it needs, except `instance` and `name`, so just be
    certain to provide a way to deal with those two, and the rest can be done
    however you like.

    `self` was not mentioned, but it still needs to be the first parameter.

    Implementing `get()`:
    `get()` is a very simple method; the only parameter is `self`, and its only
    duty is to return the current value of the property.

    Implementing `set()`:
    If you want the Delegated Property to be read-only, simply ignore
    implementing `set()`. Otherwise, know that, other than `self`, it has only
    the one other parameter, `value`, which is the new value to set the property
    to.

    Implementing for deletion (or to prevent it):
    By default, Delegated Properties can be deleted with `del`. If you don't
    want your property to be deletable, all you need to do is set an attribute
    on the property called `do_not_delete` and set it to `True`. You can also
    add the attribute and set it to `False` if you want the attribute to allow
    programatic deletability. Also, if it's possible to delete the property
    and if you want to clean up any resources, you can implement the `delete()`
    method. It takes no arguments other than `self`.

    Final Implementation Notes:
    It is recommended that the value of the property be stored on the Delegated
    Property itself, rather than trying to find a place on `instance` to store
    it. Saving on `instance` always has the chance that you'll use a clashing
    name as another attribute.

    Do not attempt to create a read-only and non-read-only version of a
    Delegated Property, or to use a read-only flag in the class which can be
    used to determine if it wants to be read-only. Rather, use the `ReadOnly`
    decorator Delegated Property to make it effectively read-only.

    Any Delegated Property instance that needs to use `set()`, even though it's
    supposed to be read-only (i.e. `LateInit`), cannot use the `ReadOnly`
    decorator and will have to implement being read-only in their own way.
    """
    def __init__(self, instance, name):
        self._name = name
        self._instance = instance

    @abstractmethod
    def get(self):
        ...

    def set(self, value):
        raise AttributeError


class DelegatedPropertyDecorator:
    def __init__(self, delegate):
        self.delegate = delegate

    @classmethod
    def of(cls, delegate):
        return compose(cls, delegate)

    def get(self):
        return self.delegate.get()

    def set(self, value):
        return self.delegate.set(value)

    def delete(self):
        self.delegate.delete()

    def __getattr__(self, item):
        if hasattr(self.delegate, item):
            return getattr(self.delegate, item)
        else:
            raise NotImplementedError

    def __setattr__(self, key, value):
        if hasattr(self.delegate, key):
            setattr(self.delegate, key, value)
        else:
            super().__setattr__(key, value)

    def __delattr__(self, item):
        if hasattr(self.delegate, item):
            delattr(self.delegate, item)
        else:
            super().__delattr__(item)


no_value = object()


class Lazy(DelegatedProperty):
    def __init__(self, initializer, **kwargs):
        super().__init__(**kwargs)
        self.value = no_value
        self.initializer = initializer

    def get(self):
        if self.value is no_value:
            self.value = self.initializer()
            self.initializer = None  # release the initializer from memory
        return self.value

    def set(self, value):
        self.value = value
        if self.initializer:
            self.initializer = None


class LateInit(DelegatedProperty):
    def __init__(self, value=no_value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def get(self):
        if self.value is no_value:
            raise AttributeError(
                "Attribute, {}, not yet initialized".format(self._name))
        else:
            return self.value

    def set(self, value):
        self.value = value


class ReadOnlyLateInit(LateInit, DelegatedProperty):
    def set(self, value):
        if self.value is no_value:
            super().set(value)
        else:
            raise AttributeError


class ByMap(DelegatedProperty):
    def __init__(self, mapping, **kwargs):
        super().__init__(**kwargs)
        self.mapping = mapping

    def get(self):
        return self.mapping[self._name]

    def set(self, value):
        self.mapping[self._name] = value


class ReadOnly(DelegatedPropertyDecorator):
    def __init__(self, delegate):
        super().__init__(delegate)
        self.do_not_delete = True

    def set(self, value):
        raise TypeError(
            "Cannot change read-only attribute, '{}'".format(self._name))


def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))