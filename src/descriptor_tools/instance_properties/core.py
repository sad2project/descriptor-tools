# coding=utf-8
from abc import ABCMeta, abstractmethod

from descriptor_tools.storage import InstanceStorage, protected

__all__ = ['InstanceProperty', 'DelegatedProperty', 'ReadOnly', 'Deletable']


class InstanceProperty:
    """
    :InstanceProperty is what makes instance properties possible, by providing
    the engine for delegated properties to run off of. :InstanceProperty
    recognizes when an attribute is being initialized on an object and assumes
    it's being given a :DelegatedProperty at that time. Otherwise, it delegates
    attribute access calls to the :DelegatedProperty for the instance.

    It should be noted that, by default, `__delete__()` fails with an
    :AttributeError. In order to delete, you need to manually call the menthod
    and pass in `allow=True` or decorate (Gang of Four style) the
    :InstanceProperty object with a :Deletable.

    i.e. `attribute = Deletable(InstanceAttribute())`
    """
    def __init__(self,
                 delegate_storage=InstanceStorage.factory(name_mangler=protected)):
        """
        Initializes an :InstanceProperty object.
        :param delegate_storage: A function that takes in a descriptor and
            returns an :InstanceStorage, :DictStorage or equivalent. The
            default factory is one that creates an :InstanceStorage that stores
            it under the name of the descriptor's attribute, but with an '_'
            prefix.
        """
        self._delegate_storage = delegate_storage(self)

    def __call__(self, instance):
        return self.__get__(instance, type(instance))

    def __set_name__(self, owner, name):
        self._delegate_storage.set_name(name)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self._delegate_storage.get(instance).get()

    def __set__(self, instance, value):
        if instance not in self._delegate_storage:
            value.set_meta(*self._meta(instance))
            self._delegate_storage.set(instance, value)
        else:
            self._delegate_storage.get(instance).set(value)

    def __delete__(self, instance, allow=False):
        if not allow:
            name = self._delegate_storage.get(instance).base_name
            raise AttributeError(
                str.format("Attribute '{}' on object {} cannot be deleted", name, self))
        self._delegate_storage.delete(instance)

    def _meta(self, instance):
        return (
            self,
            instance,
            self._delegate_storage.name(instance))


class DelegatedProperty(metaclass=ABCMeta):
    """
    A Delegated Property is the kind of property you always wanted to write; it
    only knows about and deals with a single instance of the class while
    :InstanceProperty deals with all the details that were always so difficult
    with descriptors.

    It is not required to subclass :DelegatedProperty to create one, but it does
    help label the class for what it is.

    To create a Delegated Property, you need:
    `set_meta(self, descriptor, instance, name)`
    `get(self) -> value`
    `set(self, value)`

    Implementing `set_meta()`:
    This method is called when the delegated property is added onto the Instance
    Property descriptor.
    This method takes in a few arguments. These are the `descriptor` that
    controls the delegated property, the `instance` that the delegated property
    is associated with as well as the `name` of the attribute the descriptor is
    stored under. You can use or ignore any of these however you please, but it
    is typically recommended that you store the `name` so you can use it in any
    error messages.

    Implementing `get()`:
    `get()` is a very simple method; the only parameter is `self`, and its only
    duty is to return the current value of the property.

    Implementing `set()`:
    Other than `self`, `set()` has only the one other parameter, `value`, which
    is the new value to set the property to.

    Final Implementation Notes:
    It is recommended that the value of the property be stored on the Delegated
    Property itself, rather than trying to find a place on `instance` to store
    it. Saving on `instance` always has the chance that you'll use a clashing
    name as another attribute, plus it adds yet another step of indirection.

    You can attempt to create a read-only Delegated Property by causing `set()`
    to do nothing or error out. Unless the whole point of the property is to be
    read-only, though, use the :ReadOnly wrapper on an :InstanceProperty object
    and that will take care of it as well. This way, you can design your
    properties to be mutable but still also use them in a read-only fashion.

    Any Delegated Property instance that needs to use `set()`, even though it's
    supposed to be read-only (e.g. `LateInit`), cannot use the `ReadOnly`
    decorator and will have to implement being read-only in their own way.
    """
    @abstractmethod
    def set_meta(self, descriptor, instance, name):
        ...

    @abstractmethod
    def get(self):
        ...

    @abstractmethod
    def set(self, value):
        ...


class Deletable:
    """
    :Deletable is a decorator of :InstanceProperty (Gang of Four decorator, not
    a Python decorator) that makes it so that the property can be deleted from
    an instance.

    By default, :InstanceProperty raises an AttributeError when you try to
    delete an attribute from an instance controlled by it, but wrapping it in
    an instance of this class makes it deletable.

    Example Usage:
        `attribute = Deletable(InstanceProperty())`

    Like any other proper decorator, this can be stacked with other decorators,
    such as the :ReadOnly decorator (though it's weird to allow deleting an
    attribute when you can't otherwise alter it).
    """
    def __init__(self, inst_prop):
        """
        Initializes a :Deletable instance property
        :param inst_prop: An InstanceProperty object (or equivalent) to wrap
        """
        self.delegate = inst_prop

    def __set_name__(self, owner, name):
        self.delegate.__set__name__(owner, name)

    def __call__(self, instance):
        return self.delegate(instance)

    def __get__(self, instance, owner):
        return self.delegate.__get__(instance, owner)

    def __set__(self, instance, value):
        self.delegate.__set__(instance, value)

    def __delete__(self, instance, allow=True):
        self.delegate.__delete__(instance, allow=True)


class ReadOnly:
    """
    :ReadOnly is a decorator of :InstanceProperty (Gang of Four decorator, not
    a Python decorator) that makes it so that the property cannot be changed
    from it's initial value. This helps in building immutable types.

    Example Usage:
        `attribute = ReadOnly(InstanceProperty())`

        Then, in the `__init__()`
        `self.attribute = ADelegatedProperty()`

    Like any other proper decorator, this can be stacked with other decorators,
    such as the :Deletable decorator (though it's weird to allow deleting an
    attribute when ou can't otherwise alter it).
    """
    def __init__(self, inst_prop, *, silent=False):
        """
        Initializes a :ReadOnly instance property
        :param inst_prop: An InstanceProperty object (or equivalent) to wrap
        :param silent: Defaults to `False`, meaning that if `__set__()` is ever
            called, an :AttributeError is raised. If set to `True`, the set
            operation will fail silently.
        """
        self.delegate = inst_prop
        self.silent = silent
        self.names = {}

    def __set_name__(self, owner, name):
        self.names[owner] = name
        self.delegate.__set__name__(owner, name)

    def __call__(self, instance):
        return self.delegate(instance)

    def __get__(self, instance, owner):
        return self.delegate.__get__(instance, owner)

    def __set__(self, instance, value):
        if self.silent:
            return
        name = self.names[type(instance)]
        raise AttributeError(
            str.format("Attribute '{}' on object {} is read-only", name, self))

    def __delete__(self, instance, allow=False):
        self.delegate.__delete__(instance, allow=allow)
