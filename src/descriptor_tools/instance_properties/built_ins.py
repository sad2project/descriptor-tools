# coding=utf-8
from descriptor_tools.instance_properties import DelegatedProperty


__all__ = ['Lazy', 'LateInit', 'ByMap']


no_value = object()


class Lazy(DelegatedProperty):
    """
    :Lazy defines a type of delegated property that
    """

    def __init__(self, initializer):
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
    def __init__(self, value=no_value):
        self.value = value
        self._name = None
        self._instance = None

    def set_meta(self, instance, name):
        self._name = name
        self._instance = instance

    def get(self):
        if self.value is no_value:
            raise AttributeError(
                "Attribute '{}' on object {} not yet initialized".format(
                    self._name,
                    self._instance))
        else:
            return self.value

    def set(self, value):
        self.value = value


class ByMap(DelegatedProperty):
    def __init__(self, mapping, name):
        self.mapping = mapping
        self.name = name

    def get(self):
        return self.mapping[self.name]

    def set(self, value):
        self.mapping[self.name] = value


class Validating(DelegatedProperty):
    def __init__(self, value, validator):
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
