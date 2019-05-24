# coding=utf-8
from descriptor_tools.instance_properties import DelegatedProperty


__all__ = ['Lazy', 'LateInit', 'ByMap', 'Validating']


no_value = object()


class Lazy(DelegatedProperty):
    """
    :Lazy defines a type of :DelegatedProperty that will lazily calculate the
    value of the attribute. When created, it takes a function to call with no
    arguments in order to calculate the value.

    When the value of the attribute is looked up the first time, the given
    function is called and the value it calculated is cached for simple lookup
    from then on.

    If the attribute is assigned to, the lazy calculation is ignored and the
    given value is used instead.
    """

    def __init__(self, initializer):
        """
        Create the Lazy attribute using a parameterless function that will
        produce the value upon the first lookup.
        :param initializer: parameterless function that, when run, will produce
            the desired value for the attribute
        """
        self.value = no_value
        self.initializer = initializer

    def get(self):
        if self.value is no_value:
            self.value = self.initializer()
            self.initializer = None  # release the initializer reference
        return self.value

    def set(self, value):
        self.value = value
        if self.initializer:
            self.initializer = None


class LateInit(DelegatedProperty):
    """
    :LateInit is a :DelegatedProperty that enforces that a value is supposed to
    be supplied to the attribute, but it doesn't necessarily have a value
    immediately after the holding instance is created. This could be the case
    with certain types of serializers that require the type to have a constructor
    without arguments and then sets the attribute values directly.

    :LateInit ensures a value by raising an :AttributeError when accessed before
    being given a value. So, you can test that an object with a :LateInit
    attribute was fully initialized by looking up the value and seeing if there's
    a raised error. If you know how to access the :LateInit object directly, you
    can also use its `is_invalid()` method to determine if it has a value or not.
    """

    def __init__(self, value=no_value):
        self.value = value
        self._name = None
        self._instance = None

    def set_meta(self, instance, name):
        self._name = name
        self._instance = instance

    def is_invalid(self):
        """
        :return: True if a value has not yet been set on the attribute
        """
        return self.value is no_value

    def get(self):
        if self.is_invalid():
            raise AttributeError(
                "Attribute '{}' on object {} not yet initialized".format(
                    self._name,
                    self._instance))
        else:
            return self.value

    def set(self, value):
        self.value = value


class ByMap(DelegatedProperty):
    """
    :ByMap is a :DelegatedProperty that can be used so a class can wrap a given
    dictionary.

    For example, if you have a type that is serialized and deserialized
    frequently, you may want to simplify the process somewhat by having the
    instances just store all the attributes on a dictionary that can just be
    returned for serialization and used by the constructor for deserialization.

    Normally, this would require custom `property`s that delegate to the stored
    dictionary, making for a very cluttered class definition:

        class Foo:
            def __init__(self, dictionary):
                self.dictionary = dictionary

            @property
            def bar(self):
                return self.dictionary['bar']

            @bar.setter
            def bar(self, value):
                self.dictionary['bar'] = value

    And that was just for one attribute. For each attribute you'd have to add
    two new methods to deal with lookup and setting (or just one if you only
    allow lookup, but it's still a lot).

    Instead, with :ByMap, you can do it like this:

        class Foo:

            bar = InstanceProperty()
            baz = InstanceProperty()
            qux = InstanceProperty()

            def __init__(self, dictionary):
                self.dictionary = dictionary
                self.bar = ByMap(dictionary, 'bar')
                self.baz = ByMap(dictionary, 'baz')
                self.qux = ByMap(dictionary)

    And that's with 3 attributes instead of 1. It scales much more nicely. Note
    that you can supply a key for accessing the dictionary. If you don't supply
    the key, it defaults to the name of the attribute.
    """

    def __init__(self, mapping, key=no_value):
        """
        Cneates a :ByMap :DelegatedProperty to delegate attribute calls to the
        given dictionary.
        :param mapping: dictionary to map the attribute calls to
        :param key: (optional) key in the dictionary to map to. If not given,
            defaults to the name of the attribute the :InstanceProperty is stored
            under.
        """
        self.mapping = mapping
        self.key = key

    def set_meta(self, _, name):
        if self.key == no_value:
            self.key = name

    def get(self):
        return self.mapping[self.key]

    def set(self, value):
        self.mapping[self.key] = value


class Validating(DelegatedProperty):
    """
    :Validating is a simple validating :DelegatedProperty that takes a
    validation function to make sure that any values provided is valid.

    The validation function should take the value to test as the only argument
    and return `True` if valid or `False` if invalid. Optionally, you can also
    raise an exception in order to provide a custom error when invalid.
    Otherwise, if the initial value fails, an `AttributeError` with the message
    "Failed initial validation" is raised, and at other times the
    `AttributeError` with have a message with the template "<value> is not a
    walid value for attribute '<attr name>' on object <object string>".

    It is recommended to use an `AttributeError` or something with a similar
    name to 'ValidationError' if raising a custom error.
    """

    def __init__(self, value, validator):
        """
        Creates a :Validating :DelegatedProperty that makes sure any value set
        meets the given validation rule
        :param value: Initial value for the attribute
        :param validator: Function to validate incoming values. Must require
            only one argument (the value to validate) and either return False or
            raise an exception when the value is invalid. If the value is valid,
            must return True
        :raises AttributeError or custom error from `validator` if the given
            value fails validation.
        """
        if not validator(value):
            raise AttributeError("Failed initial validation")
        self.value = value
        self.validator = validator
        self.name = None
        self.instance = None

    def set_meta(self, instance, name):
        self.instance = instance
        self.name = name

    def get(self):
        return self.value

    def set(self, value):
        if not self.validator(value):
            message = "{} is not a valid value for attribute '{}' on object {}"
            raise AttributeError(
                message.format(value, self.name, self.instance))
