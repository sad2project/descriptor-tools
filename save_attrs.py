import functools

def mangle_name(name, prefix='_', postfix=''):
    return prefix + name + postfix

def NameMangler(prefix='_', postfix=''):
    return functools.partial(mangle_name, prefix=prefix, postfix=postfix)

def set_on(instance, attrname, value):
    instance.__dict__[attrname] = value

def getdescriptor(cls, descname, *, unbound):
    attr = getattr(cls, descname)
    return attr.descriptor if unbound else attr
    
def attrset(instance, attrname, value, **ignored):
    setattr(instance, attrname, value)

def basic_descriptor_set(instance, attrname, value, *, unbound=False):
    getdescriptor(type(instance), attrname, unbound=unbound).__set__(instance, value)

def forcedset(instance, attrname, value, *, unbound=False):
    getdescriptor(type(instance), attrname, unbound=unbound).__set__(instance, value, forced=True)

def secretset(instance, attrname, value, *, secret='set', unbound=False):
    desc = getdescriptor(type(instance), attrname, unbound=unbound)
    getattr(desc, secret)(instance, value)
    
def setattribute(instance, attrname, value, *, unbound=False, strategies=(basic_descriptor_set, forcedset, secretset, attrset)):
    for strat in strategies:
        try:
            strat(instance, attrname, value, unbound=unbound)
            return
        except TypeError, AttributeError:
            continue
    raise AttributeError("Cannot set attribute '{attrname}' on instance of type '{type(instance)}'")