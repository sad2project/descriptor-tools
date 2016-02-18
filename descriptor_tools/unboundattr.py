from descriptor_tools import name_of


__all__ = ['UnboundAttribute']


DEFAULT = object()


class UnboundAttribute:
    """
    An UnboundAttribute is a similar concept to an unbound method. An unbound
    attribute is a callable that only needs an instance from which to pull
    the value from. They are generally produced by "binding" descriptors,
    although alternative implementations could be made.

    For instance, if a class, `Class` has a binding descriptor called `attr`,
    you can get an unbound attribute with `Class.attr`. Then call it with any
    instance of `Class` to get the value stored there.

        inst1 = Class()
        inst1.attr = 5
        inst2 = Class()
        inst2.attr = 4

        attr = Class.attr

        attr(inst1)
        >> 5
        attr(inst2)
        >> 4

    UnboundAttributes work especially well for providing simple keys for
    comparison and for mapping to an attribute.

        sorted_vals = vals.sort(key=Class.attr)
        mapped_vals = map(Class.attr, vals)

    UnboundAttributes can also be used to set and delete attributes on
    instances using the `set()` and `delete()` methods.
    """
    def __init__(self, descriptor, owner):
        """

        :param descriptor:
        :param owner:
        :return:
        """
        self.descriptor = descriptor
        self.owner = owner

    def __call__(self, instance):
        return self.descriptor.__get__(instance, self.owner)

    def set(self, instance, value):
        self.descriptor.__set__(instance, value)

    def delete(self, instance):
        self.descriptor.__delete__(instance)

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
