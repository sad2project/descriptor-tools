from descriptor_tools import UnboundAttribute
from descriptor_tools.decorators import (DescriptorDecoratorBase,
                                         _lifted_desc_results,
                                         is_data_desc,
                                         Binding,
                                         binding,
                                         forced,
                                         SecretSet,
                                         SetOnce,
                                         set_once,
                                         ForcedSet)
from unittest import TestCase
from tests.descriptor_tools import test_mocks as mocks


class Lifted_Desc_Results_Test(TestCase):
    def test_self_lifting(self):
        wrapped = mocks.Descriptor()
        wrapper = DescriptorDecoratorBase(None)

        result = _lifted_desc_results(wrapped, wrapper, None, object)

        self.assertIs(result, wrapper)

    def test_Unbounded_lifting(self):
        wrapped = mocks.Binding(None)
        wrapper = DescriptorDecoratorBase(wrapped)

        result = _lifted_desc_results(wrapped, wrapper, None, object)

        self.assertIs(result.descriptor, wrapper)

    def test_other(self):
        wrapped = mocks.Descriptor()
        instance = mocks.ClassWithDescriptor(wrapped)
        instance.attr = 5
        wrapper = DescriptorDecoratorBase(wrapped)

        result = _lifted_desc_results(wrapped, wrapper, instance, type(instance))

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
        wrapper = DescriptorDecoratorBase(DescriptorDecorator_Base_Test.Wrapped())

        self.assertTrue(wrapper.other_method())

    def test_doesnt_redirect_to_nonexistant_methods(self):
        wrapper = DescriptorDecoratorBase(DescriptorDecorator_Base_Test.Wrapped())

        with self.assertRaises(AttributeError):
            wrapper.non_existant_method()


class DescriptorDecorator_WrappingANonDataDescriptor_Test(TestCase):
    def setUp(self):
        self.wrapped = mocks.Stubs.NonDataDescriptor()
        self.decor = DescriptorDecoratorBase(self.wrapped)
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
        self.decor = DescriptorDecoratorBase(self.wrapped)
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
        self.decor = DescriptorDecoratorBase(mocks.Stubs.DataDescriptorWithoutDelete())
        self.instance = mocks.ClassWithDescriptor(self.decor)

    def test_delete_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.decor.__delete__(self.instance)

    def test_instance_delete_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            del self.instance.attr


class DescriptorDecorator_WrappingADataDescriptorWithoutSet(TestCase):
    def setUp(self):
        self.decor = DescriptorDecoratorBase(mocks.Stubs.DataDescriptorWithoutSet())
        self.instance = mocks.ClassWithDescriptor(self.decor)

    def test_set_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.decor.__set__(self.instance, 5)

    def test_instance_set_raises_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.instance.attr = 5


class DescriptorDecorator_WrappingADataDescriptorWithoutGet(TestCase):
    def setUp(self):
        self.decor = DescriptorDecoratorBase(mocks.Stubs.DataDescriptorWithoutGet())
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
        self.decor = DescriptorDecoratorBase(mocks.Binding(mocks.Descriptor()))
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
        self.decor.__set__(self.instance, 5, force=True)

        self.assertEqual(self.instance.attr, 5)

    def test_other_call_version(self):
        self.Class.attr.__set__(self.instance, 5, force=True)

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


class Binder:
    def __init__(self):
        self.get_called = False

    @binding
    def __get__(self, instance, owner):
        self.get_called = True
        return instance


class BindingMethod_Test(TestCase):
    class Class:
        attr = Binder()

    def test_get_by_class_retrieves_UnboundAttribute(self):
        result = self.Class.attr

        self.assertIsInstance(result, UnboundAttribute)

    def test_get_by_class_doesnt_redirect(self):
        result = self.Class.attr

        self.assertFalse(result.descriptor.get_called)

    def test_get_by_instance_redirects(self):
        instance = self.Class()

        instance.attr

        self.assertTrue(self.Class.attr.get_called)


class Forceful:
    def __init__(self):
        self.set_called = False

    @forced
    def __set__(self, instance, value):
        self.set_called = True


class SecretSetMethod_Test(TestCase):
    class Class:
        attr = Forceful()

    def test_set_fails_without_force(self):
        instance = self.Class()

        with self.assertRaises(AttributeError):
            instance.attr = 5

    def test_set_doesnt_redirect_without_force(self):
        instance = self.Class()

        try:
            instance.attr = 5
        except AttributeError:
            self.assertFalse(self.Class.attr.set_called)

    def test_set_works_with_force(self):
        instance = self.Class()

        self.Class.attr.__set__(instance, 5, forced=True)

        self.assertTrue(self.Class.attr.set_called)


class FirstTimer:
    def __init__(self):
        self.set_called = False

    @set_once
    def __set__(self, instance, value):
        self.set_called = True


class SetOnceMethod_Test(TestCase):
    class Class:
        attr = FirstTimer()

    def test_set_works_first_time(self):
        instance = self.Class()

        instance.attr = 5

        self.assertTrue(self.Class.attr.set_called)

    def test_set_doesnt_work_more_than_one_time(self):
        instance = self.Class()

        instance.attr = 5

        with self.assertRaises(AttributeError):
            instance.attr = 5




















