import tomlkit.exceptions


class TOMLConfError(Exception):
    """Base exception for tomlconf."""


class FileError(TOMLConfError, EnvironmentError):
    """TOML I/O error."""


class TOMLKitError(TOMLConfError, tomlkit.exceptions.TOMLKitError):
    """TOML Kit library error."""


class TOMLParseError(TOMLKitError, tomlkit.exceptions.ParseError):
    """Error parsing TOML."""
    def __init__(self, exc, line, col):
        self._line = line
        self._col = col

    @property
    def line(self):
        return self._line

    @property
    def col(self):
        return self._col

    def __str__(self):
        return str(self.__context__)


class NonExistentKey(KeyError, TOMLKitError):
    """A non-existent key was used."""

    def __str__(self):
        return str(self.__context__)


class KeyAlreadyPresent(TOMLKitError, tomlkit.exceptions.KeyAlreadyPresent):
    """A duplicate key was used."""

    def __str__(self):
        return str(self.__context__)
