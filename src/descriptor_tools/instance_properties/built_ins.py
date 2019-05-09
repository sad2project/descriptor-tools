# coding=utf-8
from descriptor_tools.instance_properties import DelegatedProperty


__all__ = ['Lazy', 'LateInit', 'ReadOnlyLateInit', 'ByMap', 'ReadOnly']


no_value = object()


class Lazy(DelegatedProperty):
    """
    :Lazy defines a type of delegated property that
    """

    def set_meta(self, descriptor, instance, name):
        pass

    def __init__(self, initializer, **kwargs):
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
    def __init__(self, value=no_value, *, name, **kwargs):
        self.value = value
        self.name = name

    def get(self):
        if self.value is no_value:
            raise AttributeError(
                "Attribute, {}, not yet initialized".format(self.name))
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
    def __init__(self, mapping, *, name, **kwargs):
        self.mapping = mapping
        self.name = name

    def get(self):
        return self.mapping[self.name]

    def set(self, value):
        self.mapping[self.name] = value


class ReadOnly(DelegatedProperty):
    def __init__(self, delegate):
        self.delegate = delegate

    @classmethod
    def of(cls, delegate):
        return compose(cls, delegate)

    def get(self):
        return self.delegate.get()


def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))