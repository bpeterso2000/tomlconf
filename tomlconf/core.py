import os
from pathlib import Path
from sys import argv

import tomlkit
import tomlkit.exceptions as tke

from .appdir import get_app_dir
from .errors import FileError, TOMLParseError, KeyAlreadyPresent


def parse_toml(s):
    try:
        return tomlkit.parse(s)
    except tke.KeyAlreadyPresent as e:
        raise KeyAlreadyPresent(e)
    except tke.ParseError as e:
        raise TOMLParseError(e, e.line, e.col)


def get_filename(config_path=None, roaming=True, force_posix=False):
    """Return the path/filename where the config will be stored.
    When config_path is ...
        1. Not Set:
            <appdir>/<progname>/conf.toml
        2. App Name (not a directory & doesn't have a file extension):
            <appdir>/<config_path>/conf.toml
        3. Path Name: (looks like a directory)
            <config_path>/conf.toml
        4. File Name: (has a .toml extension):
            <config_path>
    """
    cpath = Path(config_path) if config_path else None
    kwds = dict(roaming=roaming, force_posix=force_posix)

    if not config_path:
        return get_app_dir(Path(argv[0]).stem, **kwds) / 'conf.toml'
    if cpath.stem == str(cpath):
        return get_app_dir(cpath.stem, **kwds) / 'conf.toml'
    if not cpath.suffix:
        return cpath / 'conf.toml'
    if cpath.suffix == '.toml':
        return cpath
    raise ValueError('Config filename must have a ".toml" extension')


class Config:
    """File context manager
    config_path (str):
        path or file name
    mode:
        'r':  read-only (default)
        'r+': read & wite
        'w':  write-only
    encoding:
        See the codecs module for the list of supported encodings.
        The default is 'utf-8'.
    errors:
        See the documentation for codecs.register for a list of the
        permitted encoding error strings. The default is 'strict'.
    """

    def __init__(
        self, config_path=None, mode='r',
        encoding='utf-8', errors='strict',
        roaming=True, force_posix=False
    ):
        if mode not in ('r', 'r+', 'w'):
            raise ValueError(
              "File context manager mode must be 'r', 'r+' or 'w'."
            )
        self.__openfile = None
        self._mode = mode
        self.filename = get_filename(config_path, roaming, force_posix)
        self.path = Path(self.filename).parent
        self.encoding = encoding
        self.errors = errors
        self.data = tomlkit.document()

    @property
    def mode(self):
        return self._mode

    def __enter__(self):
        try:
            if not self.path.exists():
                os.makedirs(self.path)
            self.__openfile = self.filename.open(
                mode=self.mode,
                encoding=self.encoding,
                errors=self.errors
            )
            if 'r' in self.mode:
                self.data = parse_toml(self.__openfile.read())
            return self
        except EnvironmentError as e:
            raise FileError(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__openfile:
            try:
                if self.mode in ('r+', 'w'):
                    self.__openfile.seek(0)
                    self.__openfile.write(tomlkit.dumps(self.data))
                    self.__openfile.truncate()
                self.__openfile.close()
            except EnvironmentError as e:
                raise FileError(e)