# coding=utf-8
from abc import ABCMeta, abstractmethod

from descriptor_tools import name_of, DescDict

from src.descriptor_tools.decorators import binding

__all__ = ['InstanceProperty', 'by', 'by_ondesc', 'DelegatedProperty']


class OnInstanceStorageStrategy:
    def retrieve(self, instprop, instance):
        try:
            return getattr(instance, instprop._secret_name)
        except AttributeError as e:
            raise AttributeError(
                "Instance property, '{}', not yet initialized".format(instprop._name)
                ) from e

    def assign(self, instprop, delegprop, instance):
        setattr(instance, instprop._secret_name, delegprop)


class OnDescriptorStorageStrategy:
    def __init__(self):
        self.storage = DescDict()

    def retrieve(self, instprop, instance):
        try:
            return self.storage[instance]
        except KeyError as e:
            raise AttributeError(
                "Instance property, '{}', not yet initialized".format(
                    instprop._name)
            ) from e

    def assign(self, instprop, delegprop, instance):
        self.storage[instance] = delegprop


class InstanceProperty:
    """
    :InstanceProperty is what makes instance properties possible, by providing
    the engine for delegated properties to run off of. :InstanceProperty uses a
    function that instantiates a delegated property and creates one for every
    instance of the class it resides on. It then delegates the real
    functionality to the delegated property associated with the instance that
    calls upon the descriptor.

    This version of :InstanceProperty stores the associated delegated property
    on the instance under the same name as the :InstanceProperty, but with an
    underscore prefix. For example, if the :InstanceProperty was saved on the
    class as `foo`, the delegated property would be stored on the instance under
    `_foo`.

    For details about changing how :InstanceProperty stores delegated
    properties, check out the `ChangingInstanceProperty` documentation.
    """
    def __init__(self,
                 instantiator,
                 *,
                 delegate_storage=OnInstanceStorageStrategy()):
        """
        Requires a function that can take at least `instance` and `name` keyword
        arguments, if not more in order to create an instance of a delegated
        property.

        When an instance of the class that `self` resides on is
        created and initializes the property, the function will be called,
        passing in any arguments given to the initializer as well as the
        `instance` and `name` keyword arguments.

        For more information, see the :descriptor_tools.instance_property module
        documentation and :DelegatedProperty documentation.

        :param instantiator: a function for instantiating a delegated property
        """
        self._instantiator = instantiator
        self._name = None
        self._secret_name = None
        self._delegate_storage = delegate_storage

    @binding
    def __get__(self, instance, owner):
        """
        Until initialized for the instance, attempting to access the property's
        value will return an initializer
        :param instance:
        :param owner:
        :return:
        """
        self._set_name(owner)
        try:
            delegprop = self._get_deleg_prop(instance)
        except AttributeError:
            # if this happens, then the property has not yet been initialized on
            # the instance yet, which means we need to return an initializer
            return InstancePropertyInitializer(
                self,
                instance,
                self._instantiator,
                self._name)
        return delegprop.get()

    def __set__(self, instance, value):
        delegprop = self._get_deleg_prop(instance)
        try:
            delegprop.set(value)
        except AttributeError as e:
            # The property doesn't implement `set()`, so the property is
            # considered read-only .
            raise AttributeError(
                    "Cannot set new value on read-only attribute, " +
                    "'{}'".format(self._name)
                    ) from e

    def _set_name(self, owner):
        if self._name is None:
            self._name = name_of(self, owner)
            self._secret_name = '_' + self._name

    def _get_deleg_prop(self, instance):
        return self._delegate_storage.retrieve(self, instance)


def by(delegated_property_instantiation_function):
    """
    A shortcut to creating an :InstanceProperty instance, :by uses the same
    wording as the language that inspired this feature, Kotlin. If you do any of
    the customization options of :InstanceProperty, it is recommended that you
    make your own shortcut function like this one to make it easier to access
    those customized versions.

    :param delegated_property_instantiation_function: a function that
    instantiates a delegated property, just like the kind :InstanceProperty needs
    :return: an :InstanceProperty that is created using
    :delegated_property_instantiation_function
    """
    return InstanceProperty(delegated_property_instantiation_function)


def by_ondesc(delegated_property_instantiation_function):
    """
    Same as :by, but it instead has the :InstanceProperty use a different
    strategy for storing the delegated properties using :DescDict instead of on
    the instances.
    :param delegated_property_instantiation_function:
    :return:
    """
    return InstanceProperty(
            delegated_property_instantiation_function,
            delegate_storage=OnDescriptorStorageStrategy())


class InstancePropertyInitializer:
    """
    A tightly-coupled helper class that works with :InstanceProperty. Do not
    touch. Do not create your own unless you are creating your own
    instance property wrapper class that will work with this the same way.
    """
    def __init__(self, instpropdesc, instance, instantiator, name):
        self.instpropdesc = instpropdesc
        self.instantiator = instantiator
        self.instance = instance
        self.name = name

    def initialize(self, *args, **kwargs):
        delegprop = self.instantiator(
                *args, **kwargs,
                instance=self.instance,
                name=self.name)
        self.instpropdesc._delegate_storage.assign(
                self.instpropdesc,
                delegprop,
                self.instance)


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
    `__init__()` will have 2 parameters, likely a 3rd, and possibly more. The
    two gauranteed parameters are `instance` and `name`, which will be provided
    as keyword arguments, so if you don't need them, you can simply end your
    `__init__()` signature with `**kwargs` to swallow them up. If you don't just
    swallow them up, make them the last parameters. If you deem it appropriate
    to store `instance` on your delegated property, it is recommended that you
    do so using a weak reference to it to prevent circular dependencies.

    The likely third parameter is either the value the property is being
    initialized with or something that you can derive the initial value from.
    There are instances where not having an initial value is the whole point
    (see `LateInit`).

    In some rare cases, it's possible your Delegated Property will need even
    more parameters in order to be properly initialized. If this is the case,
    simply require them.

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
    @abstractmethod
    def get(self):
        ...

    def set(self, value):
        raise AttributeError
