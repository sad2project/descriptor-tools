from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import (DescriptorDecorator,
                                         lifted_desc_results,
                                         is_data_desc,
                                         Binding,
                                         SecretSet,
                                         SetOnce,
                                         ForcedSet)
from unittest import TestCase
from tests.descriptor_tools import test_mocks as mocks


class Lifted_Desc_Results_Test(TestCase):
    def test_self_lifting(self):
        wrapped = mocks.Descriptor()
        wrapper = DescriptorDecorator(None)

        result = lifted_desc_results(wrapped, wrapper, None, object)

        self.assertIs(result, wrapper)

    def test_Unbounded_lifting(self):
        wrapped = mocks.Binding(None)
        wrapper = DescriptorDecorator(wrapped)

        result = lifted_desc_results(wrapped, wrapper, None, object)

        self.assertIs(result.descriptor, wrapper)

    def test_other(self):
        wrapped = mocks.Descriptor()
        instance = mocks.ClassWithDescriptor(wrapped)
        instance.attr = 5
        wrapper = DescriptorDecorator(wrapped)

        result = lifted_desc_results(wrapped, wrapper, instance, type(instance))

        self.assertEqual(result, 5)


class Is_Data_Desc_Test(TestCase):
    def test_full_data_descriptor(self):
        self.assertTrue(is_data_desc(mocks.Stubs.FullDataDescriptor()))

    def test_data_descriptor_without_get(self):
        self.assertTrue(is_data_desc(mocks.Stubs.DataDescriptorWithoutGet()))

    def test_data_descriptor_without_set(self):
        self.assertTrue(is_data_desc(mocks.Stubs.DataDescriptorWithoutSet()))

    def test_data_descriptor_without_delete(self):
        self.assertTrue(is_data_desc(mocks.Stubs.DataDescriptorWithoutDelete()))

    def test_non_data_descriptor(self):
        self.assertFalse(is_data_desc(mocks.Stubs.NonDataDescriptor()))


class DescriptorDecorator_Base_Test(TestCase):
    class Wrapped(mocks.Descriptor):
        def other_method(self):
            return True

    def test_redirects_to_wrapped_methods(self):
        wrapper = DescriptorDecorator(DescriptorDecorator_Base_Test.Wrapped())

        self.assertTrue(wrapper.other_method())

    def test_doesnt_redirect_to_nonexistant_methods(self):
        wrapper = DescriptorDecorator(DescriptorDecorator_Base_Test.Wrapped())

        with self.assertRaises(AttributeError):
            wrapper.non_existant_method()


class DescriptorDecorator_WrappingANonDataDescriptor_Test(TestCase):
    def setUp(self):
        self.wrapped = mocks.Stubs.NonDataDescriptor()
        self.decor = DescriptorDecorator(self.wrapped)
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_get_from_class(self):
        self.assertIs(self.decor, self.decor.__get__(None, self.Class))

    def test_get_from_class_redirects(self):
        self.decor.__get__(None, self.Class)

        self.assertTrue(self.wrapped.get_called)

    def test_get_from_instance(self):
        # The NonDataDescriptor returns self regardless of whether there's an
        #  instance - typical non-data descriptors ignore instance
        self.assertIs(self.decor, self.decor.__get__(self.instance, self.Class))

    def test_get_from_instance_redirects(self):
        self.decor.__get__(self.instance, self.Class)

        self.assertTrue(self.wrapped.get_called)

    def test_set_adds_to_instance(self):
        self.decor.__set__(self.instance, 5)

        self.assertEqual(self.instance.__dict__['attr'], 5)

    def test_delete_fails(self):
        with self.assertRaises(AttributeError):
            self.decor.__delete__(self.instance)


class DescriptorDecorator_WrappingADataDescriptor_Test(TestCase):
    def setUp(self):
        self.wrapped = mocks.Stubs.FullDataDescriptor()
        self.decor = DescriptorDecorator(self.wrapped)
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_get_from_class_lifts_to_self(self):
        self.assertIs(self.decor, self.decor.__get__(None, self.Class))

    def test_get_from_class_redirects(self):
        self.decor.__get__(None, self.Class)

        self.assertTrue(self.wrapped.get_called)

    def test_get_from_instance(self):
        result = self.decor.__get__(self.instance, self.Class)

        self.assertEqual(result, self.wrapped.__get__(self.instance, self.Class))

    def test_get_from_instance_redirects(self):
        self.decor.__get__(self.instance, self.Class)

        self.assertTrue(self.wrapped.get_called)

    def test_set_does_not_add_to_instance(self):
        self.decor.__set__(self.instance, 5)

        self.assertFalse('attr' in self.instance.__dict__)

    def test_set_redirects(self):
        self.decor.__set__(self.instance, 5)

        self.assertTrue(self.wrapped.set_called)

    def test_delete_redirects(self):
        self.decor.__delete__(self.instance)

        self.assertTrue(self.wrapped.delete_called)


class DescriptorDecorator_WrappingADataDescriptorWithoutDelete(TestCase):
    def setUp(self):
        self.decor = DescriptorDecorator(mocks.Stubs.DataDescriptorWithoutDelete())
        self.instance = mocks.ClassWithDescriptor(self.decor)

    def test_delete_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.decor.__delete__(self.instance)

    def test_instance_delete_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            del self.instance.attr


class DescriptorDecorator_WrappingADataDescriptorWithoutSet(TestCase):
    def setUp(self):
        self.decor = DescriptorDecorator(mocks.Stubs.DataDescriptorWithoutSet())
        self.instance = mocks.ClassWithDescriptor(self.decor)

    def test_set_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.decor.__set__(self.instance, 5)

    def test_instance_set_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.instance.attr = 5


class DescriptorDecorator_WrappingADataDescriptorWithoutGet(TestCase):
    def setUp(self):
        self.decor = DescriptorDecorator(mocks.Stubs.DataDescriptorWithoutGet())
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_get_from_instance_returns_self(self):
        result = self.decor.__get__(self.instance, self.Class)

        self.assertIs(result, self.decor)

    def test_get_from_class_returns_self(self):
        result = self.decor.__get__(None, self.Class)

        self.assertIs(result, self.decor)


class DescriptorDecorator_WrappingABindingDescriptor(TestCase):
    def setUp(self):
        self.decor = DescriptorDecorator(mocks.Binding(mocks.Descriptor()))
        self.Class = type(mocks.ClassWithDescriptor(self.decor))

    def test_get_from_class_returns_UnboundAttribute(self):
        result = self.decor.__get__(None, self.Class)

        self.assertIsInstance(result, UnboundAttribute)

    def test_UnboundAttribute_lifts_descriptor(self):
        result = self.decor.__get__(None, self.Class)

        self.assertIs(result.descriptor, self.decor)


class Binding_Test(TestCase):
    def setUp(self):
        self.decor = Binding(mocks.Descriptor())
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

        self.instance.attr = 5

    def test_class_get_is_UnboundAttribute(self):
        result = self.Class.attr

        self.assertIsInstance(result, UnboundAttribute)

    def test_class_get_lifts_UnboundAttribute_descriptor(self):
        result = self.Class.attr

        self.assertIs(self.decor, result.descriptor)

    def test_instance_get_is_attribute(self):
        result = self.instance.attr

        self.assertEqual(result, 5)


class SecretSet_Test(TestCase):
    def setUp(self):
        self.decor = SecretSet(mocks.Descriptor())
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_normal_set_fails(self):
        with self.assertRaises(AttributeError):
            self.instance.attr = 5

    def test_special_set_works(self):
        self.decor.set(self.instance, 5)

        self.assertEqual(self.instance.attr, 5)

    def test_other_call_version(self):
        self.Class.attr.set(self.instance, 5)

        self.assertEqual(self.instance.attr, 5)

class ForcedSet_Test(TestCase):
    def setUp(self):
        self.decor = ForcedSet(mocks.Descriptor())
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_normal_set_fails(self):
        with self.assertRaises(AttributeError):
            self.instance.attr = 5

    def test_forced_call_works(self):
        self.decor.__set__(self.instance, 5, forced=True)

        self.assertEqual(self.instance.attr, 5)

    def test_other_call_version(self):
        self.Class.attr.__set__(self.instance, 5, forced=True)

        self.assertEqual(self.instance.attr, 5)


class SetOnce_Test(TestCase):
    def setUp(self):
        self.decor = SetOnce(mocks.Descriptor())
        self.instance = mocks.ClassWithDescriptor(self.decor)
        self.Class = type(self.instance)

    def test_setting_once_works(self):
        self.instance.attr = 5

        self.assertEqual(self.instance.attr, 5)

    def test_setting_twice_fails(self):
        self.instance.attr = 5

        with self.assertRaises(AttributeError):
            self.instance.attr = 5






















