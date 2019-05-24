# coding=utf-8
from descriptor_tools import name_of
from warnings import warn


__author__ = 'Jake'
__all__ = ['UnboundAttribute']


DEFAULT = object()


class UnboundAttribute:
    """
    -----------------

    Warning: :UnboundAttribute is a subpar method for implementing unbound
    attributes. It's not what the user expects, creates an extra object when
    one isn't needed, and is verbose in its usuage.

    It is generally recommended that you instead return the descriptor (since
    that's what most people expect anyway) and make the descriptor callable
    with the following implementation:

        def __call__(self, instance):
            return self.__get__(instance)

    You could also have it pass in `type(instance)` as the second argument, but
    it's better to have `__get__()` give a default of `None` to the `owner`
    argument, unless you need it for instance-based calls.

    -----------------

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
        Initialized with the descriptor to make calls on, as well as the
        owner class that this was made for.

        The descriptor should usually be the one that created this in the
        first place. See the lift_descriptor() method for an instance where
        this might not be true.

        The owner is used to get passed back into the descriptor's __get__()
        method.
        :param descriptor: descriptor that all the get, set, and delete calls
        are routed through
        :param owner: used for descriptor __get__() call and string
        representations
        """
        warn(Warning("UnboundAttribute is a subpar method of doing unbound attributes. See doc of UnboundAttribute for more details."))
        self.descriptor = descriptor
        self.owner = owner

    def __call__(self, instance):
        """
        Returns the value of the attribute that this object represents from
        the given instance.
        :param instance: instance to pull the attribute value from
        :return: the value of the attribute on *instance*
        """
        return self.descriptor.__get__(instance, self.owner)

    def set(self, instance, value):
        """
        Sets the given value to the attribute that this represents on the
        given instance using the wrapped descriptor.

        Note that this operation may fail or raise an exception if the wrapped
        descriptor doesn't support it.
        :param instance: instance to set the value for
        :param value: value to set the attribute to
        """
        self.descriptor.__set__(instance, value)

    def delete(self, instance):
        """
        Deletes the attribute that this represents from the given instance
        using the wrapped descriptor.

        Note that this operation may fail or raise an exception if the wrapped
        descriptor doesn't support it.
        :param instance: instance to delete the attribute from
        """
        self.descriptor.__delete__(instance)

    def lift_descriptor(self, descriptor):
        """
        Returns a new UnboundAttribute that uses the given descriptor instead
        of the original.

        This method was created to increase support for usirg the decorator
        pattern with descriptors. When wrapping a "binding" descriptor,
        the wrapper needs itself to be the descriptor that the
        UnboundAttribute calls. If the decorator inherits from
        #DescriptorDecorator, this is handled for you.
        :param descriptor: wrapper descriptor to switch in
        :return: the new UnboundAttribute
        """
        return UnboundAttribute(descriptor, self.owner)

    def __getattr__(self, item):
        """
        Redirects unknown attribute lookups to the wrapped descriptor
        :param item: attribute being looked up
        """
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
