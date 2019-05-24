from unittest import TestCase

from descriptor_tools.instance_properties import InstanceProperty
from descriptor_tools.instance_properties.built_ins import (
    Lazy,
    LateInit,
    ByMap,
    no_value, Validating)

init_value = -256


class LazyTest(TestCase):
    @staticmethod
    def lazy_init():
        return init_value

    def test_given_uninitialized_value_is_no_value(self):
        sut = Lazy(self.lazy_init)

        self.assertEqual(no_value, sut.value)

    def test_given_initialized_value_is_init_value(self):
        sut = Lazy(self.lazy_init)

        sut.get()

        self.assertIs(init_value, sut.value)

    def test_get_returns_init_value(self):
        sut = Lazy(self.lazy_init)

        result = sut.get()

        self.assertEqual(init_value, result)

    def test_given_initialized_value_then_initializer_is_None(self):
        sut = Lazy(self.lazy_init)

        sut.get()

        self.assertIs(sut.initializer, None)

    def test_set_assigns_new_value(self):
        sut = Lazy(self.lazy_init)
        value_set = 1

        sut.set(value_set)

        self.assertEqual(sut.value, value_set)

    def test_given_set_called_then_initializer_is_None(self):
        sut = Lazy(self.lazy_init)

        sut.set(init_value)

        self.assertIs(None, sut.initializer)


class LateInitTest(TestCase):
    def test_given_uninitialized_then_value_is_no_value(self):
        sut = LateInit()

        self.assertIs(sut.value, no_value)

    def test_given_uninitialized_when_calling_get_then_raises_exception(self):
        sut = LateInit()

        with self.assertRaises(AttributeError):
            sut.get()

    def test_given_initialized_when_calling_get_then_returns_set_value(self):
        sut = LateInit()
        sut.set(init_value)

        result = sut.get()

        self.assertEqual(result, init_value)


class ByMapTest(TestCase):
    name = "name"
    map = {name: init_value}

    def tearDown(self):
        self.map[self.name] = init_value

    def test_returns_value_from_map(self):
        sut = ByMap(self.map, key=self.name)

        result = sut.get()

        self.assertEqual(result, init_value)

    def test_set_assigns_value_to_map(self):
        sut = ByMap(self.map, key=self.name)

        sut.set(1)

        self.assertEqual(self.map[self.name], 1)

    def test_uses_attribute_name_if_no_key_given(self):
        map = {"attr": init_value}

        class Class:
            attr = InstanceProperty()

            def __init__(self, mapping):
                self.attr = ByMap(mapping)

        instance = Class(map)

        self.assertEqual(init_value, instance.attr)


class ValidatingTest(TestCase):
    @staticmethod
    def is1(val):
        return val == 1

    def test_fail_invalid_initialization(self):
        with self.assertRaises(AttributeError):
            _ = Validating(5, self.is1)

    def test_fail_invalid_set(self):
        sut = Validating(1, self.is1)
        sut.set_meta(object(), "attr")
        with self.assertRaises(AttributeError):
            sut.set(5)

    def test_valid_set_and_get_success(self):
        sut = Validating(1, self.is1)
        sut.set_meta(object(), "attr")

        sut.set(1)

        self.assertEqual(1, sut.get())
