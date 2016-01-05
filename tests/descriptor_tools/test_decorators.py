from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import GetDescDecorator, SetDescriptorDecorator
from unittest import TestCase
from tests.descriptor_tools import test_mocks as mocks


class GetDescDecorator_Test(TestCase):
    def setUp(self):
        self.instance = mocks.ClassWithDescriptor(
                              GetDescDecorator(mocks.Descriptor()))

    def test_redirects_simple_get(self):
        self.instance.attr = 5

        self.assertEqual(self.instance.attr, 5)

    def test_redirects_methods_wrapped_has(self):
        class MockWrapped:
            def check(self):
                self.called = True

        decor = GetDescDecorator(MockWrapped())

        decor.check()

        self.assertTrue(decor.called)

    def test_does_not_redirect_to_methods_wrapped_doesnt_have(self):
        class MockWrapped:
            pass

        decor = GetDescDecorator(MockWrapped())

        with self.assertRaises(AttributeError):
            decor.check

    def test_redirects_return_self(self):
        #when the wrapped descriptor returns self, the decorator returns itself
        self.assertIsInstance(type(self.instance).attr, GetDescDecorator)

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
                                GetDescDecorator(BindingDescriptor()))

        # is still sending up an UnboundAttribute as needed
        self.assertIsInstance(type(instance).attr, UnboundAttribute)
        # the UnboundAttribute's descriptor is set to the wrapper instead of
        # the wrapped descriptor
        self.assertIsInstance(type(instance).attr.descriptor, GetDescDecorator)


class SetDescDecorator_Test(TestCase):
    def test_redirects_set(self):
        pass
