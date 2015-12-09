from unittest import TestCase
import tests.descriptor_tools.test_mocks as helpers
from descriptor_tools.find_descriptors import *


class Get_Descriptor_Test(TestCase):

    def test_with_normal_descriptor_unspecified(self):
        instance = helpers.ClassWithDescriptor()

        result = get_descriptor(type(instance), "attr")

        self.assertIsInstance(result, helpers.Descriptor)

    def test_with_binding_descriptor_unspecified(self):
        instance = helpers.ClassWithBindingDescriptor()

        result = get_descriptor(type(instance), "attr")

        self.assertIsInstance(result, helpers.BindingDescriptor)

    def test_with_normal_descriptor_specified(self):
        instance = helpers.ClassWithDescriptor()

        result = get_descriptor(type(instance), "attr", binding=False)

        self.assertIsInstance(result, helpers.Descriptor)

    def test_with_binding_descriptor_specified(self):
        instance = helpers.ClassWithBindingDescriptor()

        result = get_descriptor(type(instance), "attr", binding=True)

        self.assertIsInstance(result, helpers.BindingDescriptor)

    def test_with_normal_descriptor_incorrectly_specified(self):
        instance = helpers.ClassWithDescriptor()

        with self.assertRaises(AttributeError):
            get_descriptor(type(instance), "attr", binding=True)

    def test_with_binding_descriptor_incorrectly_specified(self):
        instance = helpers.ClassWithBindingDescriptor()

        result = get_descriptor(type(instance), "attr", binding=False)

        self.assertIsInstance(result, helpers.UnboundAttribute)


