from descriptor_tools import DescDict, UnboundAttribute


class BindingDataDescriptor:
    def __init__(self):
        self.storage = DescDict()

    def __get__(self, instance, owner):
        if instance is None:
            return UnboundAttribute(self, owner)
        else:
            return self.storage[instance]

    def __set__(self, instance, value):
        self.storage[instance] = value

    def __delete__(self, instance):
        del self.storage[instance]


class NonBindingDataDescriptor:
    def __init__(self):
        self.storage = DescDict()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.storage[instance]

    def __set__(self, instance, value):
        self.storage[instance] = value

    def __delete__(self, instance):
        del self.storage[instance]


class BindingGetter:
    """
    BindingGetter is a mix-in for descriptors that allows the creator ignore
    having to deal with class access and creating UnboundAttributes.

    BindingGetter comes with its own __get__() implementation that,
    upon instance access, calls the _get(self, instance) method that
    subclasses are expected to create. Otherwise, if instance is None,
    it returns an appropriate UnboundAttribute.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__owners = {}  # TODO add owners cache to decorator?

    def __get__(self, instance, owner):
        if instance is None:
            return UnboundAttribute(self, owner)
        else:
            return self._get(instance)

    def __unbound_attribute_for(self, owner):
        if owner in self.__owners:
            return self.__owners[owner]
        else:
            ua = UnboundAttribute(self, owner)
            self.__owners[owner] = ua
            return ua