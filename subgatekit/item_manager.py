from typing import Iterable, Callable, Hashable


class ItemManager[T]:
    def __init__(
            self,
            hash_getter: Callable[[T], Hashable],
            items: Iterable[T] = None,
    ):
        self._hash_getter = hash_getter
        self._items = {}
        if items:
            for item in items:
                self.add(item)

    def add(self, item: T) -> None:
        key = self._hash_getter(item)
        if self._items.get(key) is not None:
            raise ValueError(f"Item with hash value '{key}' already exist")
        self._items[key] = item

    def get_all(self) -> list[T]:
        return list(self._items.values())

    def get(self, code: str) -> T:
        return self._items[code]

    def update(self, code: str, item: T) -> None:
        self.get(code)
        self._items[code] = item

    def remove(self, code: str) -> None:
        self._items.pop(code, None)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for item in self._items.values():
            yield item
