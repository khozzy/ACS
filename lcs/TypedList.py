import collections.abc


def _check_types(oktypes, o):
    if not isinstance(o, oktypes):
        raise TypeError("Wrong element type", o)


class TypedList(collections.abc.MutableSequence):

    def __init__(self, oktypes, *args):
        self._items = list()
        self.oktypes = oktypes

        for el in args:
            _check_types(oktypes, el)

        self._items.extend(list(args))

    def insert(self, index: int, o) -> None:
        _check_types(self.oktypes, o)
        self._items.insert(index, o)

    def __setitem__(self, i, o):
        _check_types(self.oktypes, o)
        self._items[i] = o

    def __delitem__(self, i):
        del self._items[i]

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self) -> int:
        return len(self._items)
