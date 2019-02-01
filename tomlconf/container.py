import tomlkit.exceptions as tomlkit
from tomlkit.container import Container

from .errors import KeyAlreadyPresent, NonExistentKey


class TOMLDocument(Container):
    """A TOML document."""

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except tomlkit.NonExistentKey as e:
            raise NonExistentKey(e)

    def append(self, key, item):
        try:
            super().append(key, item)
        except tomlkit.KeyAlreadyPresent as e:
            raise KeyAlreadyPresent(e)

    def remove(self, key):
        try:
            super().remove(key)
        except tomlkit.NonExistentKey as e:
            raise NonExistentKey(e)

    def item(self, key):
        try:
            return super().item(key)
        except tomlkit.NonExistentKey as e:
            raise NonExistentKey(e)