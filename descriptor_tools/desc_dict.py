from collections import MutableMapping
import weakref
from ctypes import cast, py_object

__author__ = 'Jake'
__all__ = ['DescDict']

DEFAULT = object()


def id2key(id):
    return cast(id, py_object).value


class DescDict(MutableMapping):
    """
    DescDict is a specialized dictionary for descriptors to store their instance
    attributes on themselves, though is not limited to that.

    DescDict is just like WeakKeyDictionary, except that it does not require the
    key to be hashable.

    Despite not hashing the instance, DescDict is still very efficient because
    it hashes the id of the instance to store it in a typical `dict`. Also, a
    weak reference finalizer is set up to remove the item from the dictionary
    when it is cleaned up.

    Methods that are implemented via `MutableMapping` Mixins:
    + `keys()`
    + `items()`
    + `values()`
    + `get()`
    + `__eq__()`
    + `__ne__()`
    + `pop()`
    + `popitem()`
    + `update()`
    + `setdefault()`
    """
    def __init__(self, mapping=None):
        """
        Initializes an empty dictionary, copying items from the optional mapping
        argument into itself
        :param mapping: an original mapping object to copy the items from
        """
        self.storage = {}

        if mapping is not None:
            for k, v in mapping.items():
                self.__setitem__(k, v)

    def __getitem__(self, key):
        """
        `d[key]`
        Return the item of *d* with key *key*. Raises a `KeyError` if *key* is
        not in the map
        :param key: the key to lookup up the item by
        :return: the item associated with the key
        """
        try:
            return self.storage[id(key)][0]
        except KeyError as e:
            raise AttributeError(e)

    def __setitem__(self, key, value):
        """
        `d[key] = value`
        Set `d[key]` to *value*
        :param key: the key to assign the value to
        :param value: the value to assign to the key
        """
        if key in self:
            self._update_item(id(key), value)
        else:
            self._new_item(key, value)

    def _update_item(self, keyId, value):
        _, finalizer = self.storage[keyId]
        self.storage[keyId] = (value, finalizer)

    def _new_item(self, key, value):
        finalizer = weakref.finalize(key, self.storage.__delitem__, id(key))
        self.storage[id(key)] = (value, finalizer)

    def __delitem__(self, key):
        """
        `del d[key]`
        Remove `d[key]` from *d*. Raises a `KeyError` if *key* is not in the map
        :param key: the key to remove from the map (along with its associated value)
        """
        try:
            self.storage[id(key)][1].detach()
            del self.storage[id(key)]
        except KeyError as e:
            raise AttributeError(e)

    def __iter__(self):
        """
        `iter(d)`
        This is an alias for `d.keys()`.
        :return: an iterator over the keys of this dictionary.
        """
        for keyId in self.storage:
            yield id2key(keyId)

    def __len__(self):
        """
        `len(d)`
        :return: the number of items in the dictionary
        """
        return len(self.storage)

    def __contains__(self, key):
        """
        `key in d`
        :param key:
        :return: `True` if *d* has a key *key*, else `False`
        """
        return id(key) in self.storage

    def clear(self):
        """
        Removes all items from the dictionary
        """
        while len(self) > 0:
            self.popitem()

    def __str__(self):
        """
        `str(d)`
        :return: a string representation of this dictionary
        """
        start = self.__class__.__name__ + "{"
        if len(self) > 6:
            middle = self._first_six_items()
        else:
            middle = self._all_items()

        return start + middle + '}'

    def __repr__(self):
        """
        `repr(d)`
        :return: a string representation that represents the constructor call to
        create this dictionary
        """
        if len(self) == 0:
            return self.__class__.__name__ + "()"
        else:
            start = self.__class__.__name__ + "({"
            middle = _list_map_items(self.items(), True)
            return start + middle + "})"

    def _first_six_items(self):
        shortened_collection = _take_n(self.items(), 6)
        return _list_map_items(shortened_collection) + ", ..."

    def _all_items(self):
        return _list_map_items(self.items())

    def __bool__(self):
        """
        `bool(d)`
        :return: `True` if `len(d) > 0`, else `False`
        """
        return bool(self.storage)


def _take_n(iterable, n):
    for i, item in enumerate(iterable):
        if i >= n:
            return
        else:
            yield item


def _list_map_items(items, representation=False):
    if representation:
        return ", ".join("{k}: {v}".format(k=repr(k), v=repr(v)) for k, v in items)
    else:
        return ", ".join("{k}: {v}".format(k=str(k), v=str(v)) for k, v in items)
