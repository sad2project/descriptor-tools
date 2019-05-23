import weakref
from functools import partial
from . import name_of, DescDict, id_name_of
from .decorators import binding


class DictStorage:
    def __init__(self):
        self.base_name = None
        self.store = DescDict()

    def name(self, instance, desc):
        if self.base_name is None:
            self.set_name(name_of(desc, type(instance)))
        return self.base_name

    def set_name(self, name):
        self.base_name = name

    def get(self, instance, desc):
        try:
            return self.store[instance]
        except KeyError:
            raise AttributeError(self.name(instance, desc))
            # TODO: fill out the error message better

    def set(self, instance, value):
        self.store[instance] = value

    def delete(self, instance):
        del self.store[instance]

    def __contains__(self, instance):
        return instance in self.store


def identity(name, desc): return name


def protected(name, desc): return "_"+name


def hex_desc_id(name, desc): return id_name_of(desc)


class InstanceStorage:
    # Do not use on more than one descriptor
    # Be certain to either call set_name or, if that can't be guaranteed, set
    #   the 'desc' attribute to the descriptor instance.
    def __init__(self, name_mangler=identity):
        self.desc = None
        self.base_name = None
        self._name = None
        self._mangler = name_mangler

    def name(self, instance):
        if self._name is None:
            self.set_name(name_of(self.desc, type(instance)))
        return self._name

    def set_name(self, name):
        self.base_name = name
        self._name = self._mangler(name, self)

    def get(self, instance):
        try:
            return vars(instance)[self.name(instance)]
        except KeyError:
            raise AttributeError(
                str.format("Attribute '{}' on object {} is not initialized", self.base_name, instance))
            # TODO: fill out the error message better

    def set(self, instance, value):
        vars(instance)[self.name(instance)] = value

    def delete(self, instance):
        del vars(instance)[self.name(instance)]

    def __contains__(self, instance):
        return self.name(instance) in vars(instance)