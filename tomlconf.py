import os
import sys
import re
import tomlkit
import tomlkit.exceptions

WIN = sys.platform.startswith('win')
MAC = sys.platform.startswith('darwin')

# get_app_dir is from the Click package. Visit
# http://click.pocoo.org for more information on the click library.


def stem(path):
    """
    Extracts the name of the file less the extension from the path

    :param path: the roadmap to a file
    :return: str, the name of the less the ".ext"
    """
    return os.path.splitext(os.path.basename(path))[0]


def _posixify(name):
    """
    Convert name to a posix compliant file name

    :param name:
    :return:
    """
    return '-'.join(name.split()).lower()


def get_app_dir(app_name, roaming=True, force_posix=False):
    r"""Returns the config folder for the application.

    The default behavior is to return whatever is most appropriate for the operating system.

    To give you an idea, for an app called ``"Foo Bar"``, something like
    the following folders could be returned:

    Mac OS X:
      ``~/Library/Application Support/Foo Bar``
    Mac OS X (POSIX):
      ``~/.foo-bar``
    Unix:
      ``~/.config/foo-bar``
    Unix (POSIX):
      ``~/.foo-bar``
    Win XP (roaming):
      ``C:\Documents and Settings\<user>\Local Settings\Application Data\Foo Bar``
    Win XP (not roaming):
      ``C:\Documents and Settings\<user>\Application Data\Foo Bar``
    Win 7 (roaming):
      ``C:\Users\<user>\AppData\Roaming\Foo Bar``
    Win 7 (not roaming):
      ``C:\Users\<user>\AppData\Local\Foo Bar``

    app_name (str):
        the application name.  This should be properly capitalized and
        can contain whitespace.

    roaming (bool):
        controls if the folder should be roaming or not on Windows. Has
        no affect otherwise.

    force_posix (bool):
        if this is set to `True` then on any POSIX system the folder
        will be stored in the home folder with a leading dot instead of
        the XDG config home or darwin's application support folder.
    """
    if WIN:
        key = roaming and 'APPDATA' or 'LOCALAPPDATA'
        folder = os.environ.get(key)
        if folder is None:
            folder = os.path.expanduser('~')
        return os.path.join(folder, app_name)

    if force_posix:
        return os.path.join(os.path.expanduser('~/.' + _posixify(app_name)))
    if MAC:
        return os.path.join(os.path.expanduser(
            '~/Library/Application Support'), app_name)
    return os.path.join(
        os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
        _posixify(app_name))


class TomlConfError(Exception):
    """Base exception class"""


# class FileError(TomlConfError, EnvironmentError):  # is this one really necessary?
#     """Problem reading or writing the TOML file."""


class TOMLKitError(TomlConfError, tomlkit.exceptions.TOMLKitError):
    """Base TOML Kit exception."""


class ParseError(TOMLKitError, tomlkit.exceptions.ParseError):
    """A syntax error in the TOML being parsed.
    References the line and location where error was encountered.
    """


class MixedArrayTypesError(
    ParseError, tomlkit.exceptions.MixedArrayTypesError
):
    """An array was found that had two or more element types."""


class InvalidNumberError(ParseError, tomlkit.exceptions.InvalidNumberError):
    """Invalid number."""


class InvalidDateTimeError(
    ParseError, tomlkit.exceptions.InvalidDateTimeError
):
    """Invalid datetime."""


class InvalidDateError(ParseError, tomlkit.exceptions.InvalidDateTimeError):
    """Invalid date."""


class InvalidTimeError(ParseError, tomlkit.exceptions.InvalidTimeError):
    """Invalid time."""


class InvalidNumberOrDateError(
    ParseError, tomlkit.exceptions.InvalidNumberOrDateError
):
    """Invalid number of date."""


class InvalidUnicodeValueError(
    ParseError, tomlkit.exceptions.InvalidUnicodeValueError
):
    """Invalid unicode code error."""


class UnexpectedCharError(ParseError, tomlkit.exceptions.UnexpectedCharError):
    """An unexpected character was found during parsing."""


class EmptyKeyError(ParseError, tomlkit.exceptions.EmptyKeyError):
    """An empty key was found during parsing."""


class EmptyTableNameError(ParseError, tomlkit.exceptions.EmptyTableNameError):
    """An empty table name was found during parsing."""


class UnexpectedEofError(ParseError, tomlkit.exceptions.UnexpectedEofError):
    """The TOML being parsed ended before the end of a statement."""


class NonExistentKey(TOMLKitError, tomlkit.exceptions.NonExistentKey):
    """Missing key error."""


class KeyAlreadyPresent(TOMLKitError, tomlkit.exceptions.KeyAlreadyPresent):
    """Duplicate key error."""

    def __init__(self, msg):
        m = re.search('"(.*)"', str(msg))
        key_name = m.group(1)
        super(KeyAlreadyPresent, self).__init__(key_name)


class ModeError(ValueError, TomlConfError):
    """
    Config File Open Mode Error.

    File context manager mode must be 'r', 'r+' or 'w'.
    """

    def __init__(self, mode):
        msg = 'File mode must be "r", "r+" or "w" not %s' % mode
        super(ModeError, self).__init__(msg)


class Config:
    """File context manager

    filename (str):
        path or file name
    mode:
        'r':  read-only (default)
        'r+': read & write
        'w':  write-only
    encoding:
        See the codecs module for the list of supported encodings.
        The default is 'utf-8'.
    errors:
        See the documentation for codecs.register for a list of the
        permitted encoding error strings. The default is 'strict'.
    """

    def __init__(self, filename=None, mode='r', encoding='utf-8', errors='strict', roaming=True, force_posix=False):
        if not filename:
            self.filename = get_app_dir(stem(sys.argv[0]), roaming=roaming, force_posix=force_posix)
        else:
            self.filename = filename
        if mode not in ('r', 'r+', 'w'):
            raise ModeError('"%s"' % mode)
        self.__openfile = None
        self._mode = mode
        self.path = os.path.split(self.filename)[0]
        self.encoding = encoding
        self.errors = errors
        self.data = tomlkit.document()

    @property
    def mode(self):
        return self._mode

    def __enter__(self):
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            self.__openfile = open(
                self.filename,
                mode=self.mode,
                encoding=self.encoding,
                errors=self.errors
            )
            if 'r' in self.mode:
                self.data = tomlkit.parse(self.__openfile.read())
        # except FileNotFoundError as e:
        #     # self.data = tomlkit.document()
        #     raise FileError(e)
        except tomlkit.exceptions.KeyAlreadyPresent as e:
            raise KeyAlreadyPresent(e)
        except (EnvironmentError, TOMLKitError) as e:
            raise TomlConfError('', e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.filename, self.mode, self.__openfile)
        if self.__openfile:
            try:
                if self.mode in ('r+', 'w'):
                    print(self.filename, file=sys.stderr)
                    self.__openfile.seek(0)
                    self.__openfile.write(tomlkit.dumps(self.data))
                    self.__openfile.truncate()
            except (EnvironmentError, TOMLKitError) as e:
                raise TomlConfError(original_exception=e)
            finally:
                self.__openfile.close()


if __name__ == '__main__':
    my_config = Config(mode='q')
    try:
        my_config = Config(mode='q')
    except TomlConfError as e:
        print('An error occured opening config file')
        sys.exit(1)
