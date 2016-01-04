from unittest import TestCase
from tests.descriptor_tools.test_mocks import Descriptor, Binding
from descriptor_tools import UnboundAttribute


class Class:
    descAttr = Descriptor()


class UnboundAttr_Test(TestCase):
    def test_creation(self):
        unboundattr = UnboundAttribute(Class.descAttr, Class)
    

