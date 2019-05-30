# coding=utf-8
from abc import ABCMeta, abstractmethod

from descriptor_tools.storage import InstanceStorage, protected

__all__ = ['InstanceProperty', 'DelegatedProperty']


_use_default = object()


def _default_of(argument, default_factory):
    if argument is _use_default:
        return default_factory()
    else:
        return argument


def _default_storage():
    return InstanceStorage(name_mangler=protected)


class InstanceProperty:
    """
    :InstanceProperty is what makes instance properties possible, by providing
    the engine for delegated properties to run off of. :InstanceProperty
    recognizes when an attribute is being initialized on an object and assumes
    it's being given a :DelegatedProperty at that time. Otherwise, it delegates
    attribute access calls to the :DelegatedProperty for the instance.

    It should be noted that, by default, `__delete__()` fails with an
    :AttributeError. In order to delete, you need to set the keyword-only
    parameter, `deletable` to `True`.

    You can also make a property be read-only (other than when initializing the
    value) by setting the `readonly` keyword-only parameter to `True`.

    When using an :InstanceProperty, you create a class-level attribute and
    assign the :InstanceProperty to that, just like any other descriptor:

        class Example:
            attr = InstanceProperty(deletable=True)

    Then, in `__init__()`, you assign a :DelegatedPropery instance to it:

        ...
            def __init__(self, someval):
                self.attr = Validating(someval, is_numeric)

    In this case, :Validating is the :DelegatedProperty type. It doesn't
    strictly have to be done in `__init__()`; it simply needs to be done when
    it is first being assigned to. Also, if you make an attribute deletable,
    the first time you assign to the attribute after it's deleted, it needs to
    be assigned a :DelegatedProperty

    At all other times, you assign to the attribute completely normally:

        inst = Example(5)
        ...
        print(inst.attr)  # prints 5
        ...
        inst.attr = 6

    And these values will be delegated to the :DelegatedProperty (hence the
    name) to deal with. Most - if not all - delegated properties store the
    value within itself, but this is not strictly necessary. For example, it
    could save the value in a database or a file, but caching it on the
    property is still usually desired.

    :InstanceProperty also works as an unbound attribute, similarly to unbound
    methods. This means that using the class version of the property will
    effectively work like using an `attrgetter` from the `operator` module. For
    example:

        # continuing with the example from above
        exattr = Example.attr  # returns the "attrgetter"
        print(exattr(inst))  # prints 6

    At this time, this is implemented without any extra objects. `__get__()`
    returns `self` when called without an instance and :InstanceProperty is a
    callable type that, when called with an instance, returns the same result
    as calling `__get__()` with an instance (which is what happens when you
    access `inst.attr` in our examples).
    """

    def __init__(self, storage=_use_default, *, readonly=False, deletable=False):
        """
        Initializes an :InstanceProperty object.
        :param storage: An :InstanceStorage, :DictStorage or equivalent. By
            default, this creates an :InstanceStorage that stores it under the
            name of the descriptor's attribute, but with an '_' prefix.
            e.g. 'attr' becomes '_attr'
        """
        self._delegates = _default_of(storage, _default_storage)
        self._delegates.desc = self

        self.readonly = readonly
        self.deletable = deletable

    def __call__(self, instance):
        return self.__get__(instance)

    def __set_name__(self, owner, name):
        self._delegates.set_name(name)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self._delegates[instance].get()

    def __set__(self, instance, value):
        # uninitialized case - value is the delegate
        if instance not in self._delegates:
            value.set_meta(*self._meta(instance))
            self._delegates[instance] = value
        # initialized and read-only case
        elif self.readonly:
            name = self._delegates.base_name
            message = "You cannot change attribute '{}' on object {} because it is read-only"
            raise AttributeError(
                message.format(name, instance)
            )
        # initialized and writeable case - value is the property value
        else:
            self._delegates[instance].set(value)

    def __delete__(self, instance):
        if not self.deletable:
            name = self._delegates.base_name
            raise AttributeError(
                "Attribute '{}' on object {} cannot be deleted".format(
                    name,
                    instance))
        del self._delegates[instance]

    def _meta(self, instance):
        return (
            instance,
            self._delegates.base_name)


class DelegatedProperty(metaclass=ABCMeta):
    """
    A Delegated Property is the kind of property you always wanted to write; it
    only knows about and deals with a single instance of the class while
    :InstanceProperty deals with all the details that were always so difficult
    with descriptors.

    It is not required to subclass :DelegatedProperty to create one, but it does
    help label the class for what it is. Also, not subclassing means that you
    will need to make a `set_meta()` method no matter what, even if it's a
    no-op method.

    To create a Delegated Property, you need:
    `set_meta(self, instance, name)`
    `get(self) -> value`
    `set(self, value)`

    Implementing `set_meta()` (optional):
    This method is called when the delegated property is added onto the Instance
    Property descriptor.
    This method takes in a few arguments. These are the `instance` that the
    delegated property is associated with as well as the `name` of the attribute
    the descriptor is stored under. You can use or ignore any of these however
    you please, but it is typically recommended that you store the `name` so you
    can use it in any error messages, if you have any. The convention of this
    library is to use both in error messages. For example, the error message
    for attempting to write to a read-only attribute is "You cannot change
    attribute '<attribute name>' on object <object string> because it is read-
    only"

    Implementing `get()`:
    `get()` is a very simple method; the only parameter is `self`, and its only
    duty is to return the current value of the property.

    Implementing `set()`:
    Other than `self`, `set()` has only the one other parameter, `value`, which
    is the new value to set the property to.e

    Final Implementation Notes:
    It is recommended that the value of the property be stored on the Delegated
    Property itself, rather than trying to find a place on `instance` to store
    it. Saving on `instance` always has the chance that you'll use a clashing
    name as another attribute, plus it adds yet another step of indirection.
    """

    def set_meta(self, instance, name):
        pass

    @abstractmethod
    def get(self):
        ...

    @abstractmethod
    def set(self, value):
        ...
