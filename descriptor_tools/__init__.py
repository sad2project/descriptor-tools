from descriptor_tools.desc_dict import DescDict
from descriptor_tools.find_descriptors import (get_descriptor_from,
                                               get_descriptor)
from descriptor_tools.names import name_of, id_name_of
from descriptor_tools.set_attrs import (AttributeSetter, mangle_name,
                                        NameMangler, set_on, setattribute,
                                        Setter)
from descriptor_tools.unboundattr import UnboundAttribute

# does not automatically export the decorators or mixins modules

__all__ = ['AttributeSetter',
           'DescDict',
           'get_descriptor',
           'get_descriptor_from',
           'mangle_name',
           'NameMangler',
           'name_of',
           'id_name_of',
           'set_on',
           'setattribute',
           'Setter',
           'UnboundAttribute']
