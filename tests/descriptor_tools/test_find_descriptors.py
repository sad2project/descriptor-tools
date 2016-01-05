from unittest import TestCase
import tests.descriptor_tools.test_mocks as mocks
from descriptor_tools import get_descriptor_from, get_descriptor, name_of

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


class Class:
    descattr = mocks.Descriptor()
    attrname = 'descattr'


class SubClass(Class):
    pass


class Name_Of_Test(TestCase):
    def test_find_name_on_class(self):
        result = name_of(Class.descattr, Class)

        self.assertEqual(result, Class.attrname)

    def test_find_name_on_sub_class(self):
        result = name_of(SubClass.descattr, SubClass)

        self.assertEqual(result, SubClass.attrname)
