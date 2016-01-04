from unittest import TestCase
import tests.descriptor_tools.test_mocks as mocks
from descriptor_tools import get_descriptor, get_descriptor_from

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


class Get_Descriptor_From_Test(TestCase):
    def test_with_normal_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor_from(instance, attrname)

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_unspecified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor_from(instance, attrname)

        self.assertIsInstance(result, mocks.Binding)

    def test_with_normal_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Descriptor())

        result = get_descriptor_from(instance, attrname, binding=False)

        self.assertIsInstance(result, mocks.Descriptor)

    def test_with_binding_descriptor_specified(self):
        instance = mocks.ClassWithDescriptor(mocks.Binding(mocks.Descriptor()))

        result = get_descriptor_from(instance, attrname, binding=True)

        self.assertIsInstance(result, mocks.Binding)
