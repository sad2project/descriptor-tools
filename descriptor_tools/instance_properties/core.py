# coding=utf-8
from descriptor_tools import name_of, binding


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

    If you would prefer to use a different name, you could create a subclass of
    :InstanceProperty and override :__set_name.

    If you would prefer to store the delegated property in a completely
    different way, you should create a delegated property storage strategy class
    and pass in an instance to the keyword argument `delegate_storage`.

    For more details about changing how :InstanceProperty works, check out the
    `ChangingInstanceProperty` documentation.
    """
    def __init__(self, instantiator, *, delegate_storage=OnInstanceStorageStrategy()):
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

    def _assign_delegate(self, delegprop, instance):
        self._delegate_storage.assign(self, delegprop, instance)

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
            return InstancePropertyInitializer(self, instance, self._instantiator, self._name)
        return delegprop.get()

    def __set__(self, instance, value):
        delegprop = self._get_deleg_prop(instance)
        try:
            delegprop.set(value)
        except AttributeError as e:
            # The property doesn't implement `set()`, so the property is
            # considered read-only .
            raise AttributeError(
                "Cannot set new value on read-only attribute, '{}'".format(self._name)
                ) from e

    def _set_name(self, owner):
        if self._name is None:
            self._name = name_of(self, owner)
            self._secret_name = '_' + self._name

    def _get_deleg_prop(self, instance):
        return self._delegate_storage.retrieve(self, instance)


def by(delegated_property_instantiation_function):
    return InstanceProperty(delegated_property_instantiation_function)


class InstancePropertyInitializer:
    def __init__(self, instpropdesc, instance, instantiator, name):
        self.instpropdesc = instpropdesc
        self.instantiator = instantiator
        self.instance = instance
        self.name = name

    def initialize(self, *args, **kwargs):
        delegprop = self.instantiator(*args, **kwargs, instance=self.instance, name=self.name)
        self.instpropdesc._assign_delegate(delegprop, self.instance)