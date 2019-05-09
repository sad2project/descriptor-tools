import weakref
from functools import partial
from . import name_of, DescDict, id_name_of
from .decorators import binding


class DictStorage:
    def __init__(self, desc):
        self.desc = desc
        self.base_name = None
        self._name = None
        self.store = DescDict()

    @classmethod
    def factory(cls):
        return lambda desc: cls(desc)

    def name(self, instance):
        if self.base_name is None:
            self.set_name(name_of(self.desc, type(instance)))
        return self.base_name

    def set_name(self, name):
        self.base_name = name

    def get(self, instance):
        try:
            return self.store[instance]
        except KeyError:
            raise AttributeError(self.name(instance))
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
    def __init__(self, desc, name_mangler=identity):
        self.desc = desc
        self.base_name = None
        self._name = None
        self._mangler = name_mangler

    @classmethod
    def factory(cls, name_mangler=identity):
        return lambda desc: cls(desc, name_mangler)

    def name(self, instance):
        if self._name is None:
            self.set_name(name_of(self.desc.object, type(instance)))
        return self._name

    def set_name(self, name):
        self.base_name = name
        self._name = self._mangler(name, self)

    def get(self, instance):
        try:
            return vars(instance)[self.name(instance)]
        except KeyError:
            raise AttributeError(self.base_name)
            # TODO: fill out the error message better

    def set(self, instance, value):
        vars(instance)[self.name(instance)] = value

    def delete(self, instance):
        del vars(instance)[self.name(instance)]

    def __contains__(self, instance):
        return self.name(instance) in vars(instance)