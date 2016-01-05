from descriptor_tools import name_of


__all__ = ['UnboundAttribute']


DEFAULT = object()


class UnboundAttribute:
    # TODO: change to SetOnceAttribute
    def __init__(self, descriptor, owner):
        self.descriptor = descriptor
        self.owner = owner

    def __call__(self, instance):
        return self.descriptor.__get__(instance, self.owner)

    def set(self, instance, value):
        self.descriptor.__set__(instance, value)

    def lift_descriptor(self, descriptor):
        return UnboundAttribute(descriptor, self.owner)

    def __getattr__(self, item):
        return getattr(self.descriptor, item)

    def __str__(self):
        attrname = name_of(self.descriptor, self.owner)
        return "Unbound Attribute '{cls}.{attr}'".format(
                                    cls=self.owner.__name__, attr=attrname)

    def __repr__(self):
        selfname = type(self).__name__
        descrep = repr(self.descriptor)
        ownerrep = repr(self.owner)
        return "{cls}({desc}, {owner})".format(cls=selfname, desc=descrep,
                                               owner=ownerrep)
