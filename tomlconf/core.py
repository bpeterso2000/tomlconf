import os
import sys
import re
import tomlkit
import tomlkit.exceptions

from .errors import FileError, TOMLParseError, KeyAlreadyPresent

WIN = sys.platform.startswith('win')
MAC = sys.platform.startswith('darwin')


# get_app_dir is from the Click package. Visit
# http://click.pocoo.org for more information on the click library.

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


def parse_toml(s):
    try:
        return tomlkit.parse(s)
    except tomlkit.exceptions.KeyAlreadyPresent as e:
        raise KeyAlreadyPresent(e)
    except tomlkit.exceptions.ParseError as e:
        raise TOMLParseError(e, e.line, e.col)


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
                os.path.join(self.path, self.filename),
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
        print(self.filename, self.mode, self.__openfile)
        if self.__openfile:
            try:
                if self.mode in ('r+', 'w'):
                    self.__openfile.seek(0)
                    self.__openfile.write(tomlkit.dumps(self.data))
                    self.__openfile.truncate()
                self.__openfile.close()
            except EnvironmentError as e:
                raise FileError(e)
