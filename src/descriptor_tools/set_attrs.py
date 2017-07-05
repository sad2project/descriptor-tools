# coding=utf-8
import functools
from . import get_descriptor_from


# --------------------------------
# functions for descriptors to use
# --------------------------------
def mangle_name(name, prefix='', postfix=''):
    """
    "Mangles" *name* by putting a *prefix* and *postfix* around it.
    :param name: name to mangle
    :param prefix: *optional* - defaults to '' - prefix to put at the beginning
    of the name to mangle it
    :param postfix: *optional* - defaults to '' - postfix to put at the ending
    of the name to mangle it
    :return: prefix + name + postfix
    """
    return prefix + name + postfix


def NameMangler(prefix='', postfix=''):
    """
    Creates a callable that will mangle a given name with the preset *prefix*
    and *postfix* given
    :param prefix: *optional* - defaults to '' - prefix to put at the beginning
    of the name to mangle it
    :param postfix: *optional* - defaults to '' - postfix to put at the ending
    of the name to mangle it
    :return: a callable that takes a name to mangle with *prefix* and *postfix*
    """
    return functools.partial(mangle_name, prefix=prefix, postfix=postfix)


def set_on(instance, attrname, value):
    """
    A cleaner, slightly shorter way of setting values directly on an instance's
    `__dict__`.
    :param instance: instance to store the value on
    :param attrname: name of the attribute to store the value with
    :param value: value to store on the instance
    """
    instance.__dict__[attrname] = value


# ---------------------------------------------------
# functions for classes to use with their descriptors
# ---------------------------------------------------
class Setter:
    """
    A collection of functions for setting different kinds of attributes on an
    instance. They can be called individually, or they can be used with
    `setattribute()` or `AttributeSetter`.
    """
    @staticmethod
    def basic(instance, attrname, value, **_):
        """
        Sets the value on the instance using `setattr()`
        :param instance: instance to store the value on
        :param attrname: name of the attribute to store the value with
        :param value: value to store for the instance
        """
        setattr(instance, attrname, value)

    @staticmethod
    def forced(instance, attrname, value, **_):
        """
        Sets the value for the instance on a forced-set descriptor attribute
        :param instance: instance to store the value on
        :param attrname: name of the attribute to store the value with
        :param value: value to store for the instance
        """
        desc = get_descriptor_from(instance, attrname)
        desc.__set__(instance, value, force=True)

    @staticmethod
    def secret(instance, attrname, value, *, secret='set', **_):
        """
        Sets the value for the instance on a secret-set descriptor attribute
        :param instance: instance to store the value on
        :param attrname: name of the attribute to store the value with
        :param value: value to store for the instance
        :param secret: *optional* - defaults to 'set' - name of the secret set
        method on the descriptor
        """
        desc = get_descriptor_from(instance, attrname)
        getattr(desc, secret)(instance, value)


def setattribute(
        instance, attrname, value, *,
        setters=(Setter.forced, Setter.secret, Setter.basic), **kwargs):
    """
    Will attempt multiple different ways to set the *value* on/for the instance
    until one works.
    Cycles through all the `Setter` methods, doing `forced`, `secret`, `basic`,
    then `inst_dict`, stopping when one of them works. This can be changed by
    providing your own iterable of functions to *setters* that have the
    following signature:

        fun(instance, attrname, value, **kwargs)

    It must be able to accept keyword arguments to handle the potential arguments
    that will be passed to other potential setter functions. For example,
    `Setter.secret()` takes a *secret* argument. If you provide a new setter
    function that takes additional parameters, you must either provide it
    with default values or else be certain to provide those arguments in the
    keyword arguments of calling this function.
    :param instance: instance to store the value on
    :param attrname: name of the attribute to store the value with
    :param value: value to store for the instance
    :param setters: *optional* - iterable of appropriate functions to attempt
    calling to set the value
    :param kwargs: *optional* - keyword arguments that will be passed into each
    of the *setters*
    """
    for setter in setters:
        try:
            setter(instance, attrname, value, **kwargs)
            return
        except (TypeError, AttributeError):
            continue
    raise AttributeError("Cannot set attribute '{attrname}' on attr of type"
                         "'{type(attr)}'")


class AttributeSetter:
    """
    Class for registering all the different descriptors and the proper ways to
    set values on them.
    Once created on the instance, the descriptors can be registered using
    `register()`. Then, to assign values to those descriptors, you can either
    call the `set()` method, providing the attribute name and new value, along
    with any potential keyword arguments to pass to the setter function provided
    in registration *or* you can set the attribute by setting the attribute as
    if it were an attribute on this class.
    For example:

        class Example:
            attr1 = SecretSetDescriptor()
            attr2 = BasicDescriptor()

            def __init__(self, attr1, attr2):
                self.setter = AttributeSetter(self)

                setter.register('attr1', Setter.secret, secret='set')
                setter.register('attr2', Setter.basic)

                # using set() to set the attribute
                setter.set('attr1', value1)
                # using attribute redirection
                setter.attr2 = value2

    This simplifies complicated descriptor setting by making all attempts the
    same as well as clean.
    """
    def __init__(self, instance, attributes=None):
        """
        Creates an `AttributeSetter` that sets to the given instance.
        Optionally, attributes can be registered in the constructor by passing
        in a mapping with the attribute names as the keys with a
        :param instance: instance to store the attributes for
        :param attributes: preregistered attributes
        :return: new `AttributeSetter`
        """
        self.instance = instance
        self.attributes = {}
        if attributes is not None:
            self.attributes.update(attributes)

    def register(self, attrname, setter, **kwargs):
        """
        Register an attribute so this can set values on it
        :param attrname: name of the attribute to register
        :param setter: the function to call to set the value
        :param kwargs: any additional arguments to pass into *setter*
        """
        self.attributes[attrname] = (setter, kwargs)

    def set(self, attrname, value, **kwargs):
        """
        Set *value* on the attribute on the instance with the given attribute
        name. If the attribute is unregistered, it will attempt to set it using
        `setattribute()` with its default setters, passing along the keyword
        arguments.
        :param attrname: name of the attribute to store the value with
        :param value: value to store on the attribute
        :param kwargs: *optional* - any additional arguments to provide to
        setters that are called
        """
        if attrname in self.attributes:
            self._set_registered(attrname, value, **kwargs)
        else:
            setattribute(self.instance, attrname, value, **kwargs)

    def _set_registered(self, attrname, value, **newkwargs):
        setter, kwargs = self.attributes[attrname]
        kwargs.update(newkwargs)
        setattribute(self.instance, attrname, value, setters=(setter,),
                     **kwargs)

    def __setattr__(self, attrname, value):
        """
        s.attrname = value
        Redirects to s.set('attrname', value)
        :param attrname: name of the attribute to store the value with
        :param value: value to store on the attribute
        """
        self.set(attrname, value)

    def __str__(self):
        return 'Attribute Setter for ' + str(self.instance)

    def __repr__(self):
        instance_text = repr(self.instance)
        attribute_text = ', ' +repr(self.attributes) if len(self.attributes) != 0 else ""
        return 'AttributeSetter(' + instance_text + attribute_text + ')'