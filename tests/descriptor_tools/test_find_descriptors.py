from unittest import TestCase
import tests.descriptor_tools.test_mocks as mocks
from descriptor_tools.find_descriptors import *

attrname = mocks.attrname
class Get_Descriptor_Test(TestCase):

    def test_with_normal_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor(type(instance), attrname)

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor(type(instance), attrname)

        self.assertIsInstance(result, mocks.Binding)

    def test_with_normal_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor(type(instance), attrname, binding=False)

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor(type(instance), attrname, binding=True)

        self.assertIsInstance(result, mocks.Binding)

    def test_with_normal_descriptor_incorrectly_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        with self.assertRaises(AttributeError):
            get_descriptor(type(instance), attrname, binding=True)

    def test_with_binding_descriptor_incorrectly_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor(type(instance), attrname, binding=False)

        self.assertIsInstance(result, mocks.UnboundAttribute)
