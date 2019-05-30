from abc import ABC, abstractmethod

from . import name_of, DescDict, id_name_of


__author__ = 'Jake'
__all__ = ['DescriptorStorage', 'InstanceStorage', 'DictStorage', 'identity',
           'protected', 'hex_desc_id']
# TODO: document


class DescriptorStorage(ABC):
    """
    :DescriptorStorage is an abstract base class of a set of classes that are
    meant to store data for descriptors. Their primary usage is like using a
    dictionary with the instance as the key, but they also have a few extra
    pieces that make using them in descriptors a little easier. For one, they
    can provide proper `AttributeError`s instead of `KeyError`s so descriptors
    may not need to. Secondly, the storage also stores the attribute name for
    the descriptor.

    To accomplish these, though, there are certain rules that have to be followed.
    The first two are easy, and are likely what you were doing to begin with:

    1. An instance of a :DescriptorStorage can only be used on a single
        descriptor
    2. The descriptor instance the :DescriptorStorage is used on must only be
        used on a single class

    The third rule is much less obvious, but can be pretty easy:

    3. In order for the :DescriptorStorage instance to get the name of the
        attribute the descriptor is stored on, one of three things must happen:

        + `set_name()` must be called by the descriptor before any of the other
            methods. A great time to use this is in the descriptor's
            `__set_name__()` method, but that's not available in versions before
            3.6.
        + The instance of the descriptor must be passed into the constructor.
            This should work if the :DescriptorStorage is being hard-coded into
            the descriptor, but it's impossible if the :DescriptorStorage is
            being injected into the descriptor's constructor, like for
            `descriptor_tools.instance_properties.InstanceProperty`s. Thus, the
            third option.
        + The instance of the descriptor must be assigned to the `desc` attribute
            of the :DescriptorStorage before any methods are called.

    Those options are in order of preference. If the descriptor you're writing
    will only be used in versions 3.6+, then you'd only need to use `set_name()`
    from a `__set_name__()` method. If it will be used in a variety of versions
    (minimum version for this library is 3.3), then I would still include that
    (it's the most effecient way) as well as one of the ways of setting the
    `desc` attribute.
    """
    def __init__(self, desc=None):
        self.desc = desc
        self.base_name = None

    def name(self, instance):
        if self.base_name is None:
            self.set_name(name_of(self.desc, type(instance)))
        return self.base_name

    def set_name(self, name):
        self.base_name = name

    @abstractmethod
    def __getitem__(self, instance):
        ...

    @abstractmethod
    def __setitem__(self, instance, value):
        ...

    @abstractmethod
    def __delitem__(self, instance):
        ...

    @abstractmethod
    def __contains__(self, instance):
        ...

    def _raiseNoAttr(self, instance):
        msg = str.format("Attribute '{}' does not exist on object {}", self.base_name, instance)
        raise AttributeError(msg)


class DictStorage(DescriptorStorage):
    def __init__(self, desc=None):
        super().__init__(desc)
        self.store = DescDict()

    def __getitem__(self, instance):
        try:
            return self.store[instance]
        except KeyError:
            self._raiseNoAttr(instance)

    def __setitem__(self, instance, value):
        self.store[instance] = value

    def __delitem__(self, instance):
        try:
            del self.store[instance]
        except KeyError:
            self._raiseNoAttr(instance)

    def __contains__(self, instance):
        return instance in self.store


def identity(name, _): return name


def protected(name, _): return "_"+name


def hex_desc_id(_, desc): return id_name_of(desc)


class InstanceStorage(DescriptorStorage):
    # Do not use on more than one descriptor
    # Be certain to either call set_name or, if that can't be guaranteed, set
    #   the 'desc' attribute to the descriptor instance.
    """
    :InstanceStorage is a type of :DescriptorStorage that stores the value on the
    instance itself. As a :DescriptorStorage, usage of the :InstanceStorage must
    follow the strict guidelines provided in the :DescriptorStorage documentation.
    """

    def __init__(self, name_mangler=identity, desc=None):
        """

        :param name_mangler:
        :param desc:
        """
        super().__init__(desc)
        self._name = None
        self._mangler = name_mangler

    def name(self, instance):
        if self._name is None:
            super().name(instance)
        return self._name

    def set_name(self, name):
        super().set_name(name)
        self._name = self._mangler(name, self)

    def __getitem__(self, instance):
        try:
            return vars(instance)[self.name(instance)]
        except KeyError:
            self._raiseNoAttr(instance)

    def __setitem__(self, instance, value):
        vars(instance)[self.name(instance)] = value

    def __delitem__(self, instance):
        try:
            del vars(instance)[self.name(instance)]
        except KeyError:
            self._raiseNoAttr(instance)

    def __contains__(self, instance):
        return self.name(instance) in vars(instance)
