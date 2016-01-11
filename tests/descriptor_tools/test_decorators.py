from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import DescriptorDecorator
from unittest import TestCase
from tests.descriptor_tools import test_mocks as mocks


class DescriptorDecorator_Test(TestCase):
    def setUp(self):
        self.instance = mocks.ClassWithDescriptor(
                              DescriptorDecorator(mocks.Descriptor()))
        self.descriptor = type(self.instance).attr

    def test_redirects_simple_get(self):
        self.descriptor.desc.__set__(self.instance, 5)

        self.assertEqual(self.instance.attr, 5)

    def test_doesnt_set_on_instance(self):
        self.instance.attr = 5

        with self.assertRaises(KeyError):
            self.instance.__dict__['attr']

    def test_redirects_methods_wrapped_has(self):
        class MockWrapped:
            def check(self):
                self.called = True

        decor = DescriptorDecorator(MockWrapped())

        decor.check()

        self.assertTrue(decor.called)

    def test_does_not_redirect_to_methods_wrapped_doesnt_have(self):
        class MockWrapped:
            pass

        decor = DescriptorDecorator(MockWrapped())

        with self.assertRaises(AttributeError):
            decor.check

    def test_redirects_return_self(self):
        # when the wrapped descriptor returns self, the decorator returns itself
        # instead of the wrapped descriptor
        self.assertIsInstance(type(self.instance).attr, DescriptorDecorator)

    def test_redirects_unbound_attribute(self):
        class BindingDescriptor:
            def __init__(self):
                self.storage = {}
            def __get__(self, instance, owner):
                if instance is None:
                    return UnboundAttribute(self, owner)
                else:
                    return self.storage[instance]
            def __set__(self, instance, value):
                self.storage[instance] = value

        instance = mocks.ClassWithDescriptor(
                                DescriptorDecorator(BindingDescriptor()))

        # is still sending up an UnboundAttribute as needed
        self.assertIsInstance(type(instance).attr, UnboundAttribute)
        # the UnboundAttribute's descriptor is set to the wrapper instead of
        # the wrapped descriptor
        self.assertIsInstance(type(instance).attr.descriptor, DescriptorDecorator)
