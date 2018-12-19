import os
import sys
import tomlkit
import tomlkit.exceptions

from .errors import FileError, TOMLParseError, KeyAlreadyPresent

WIN = sys.platform.startswith('win')
MAC = sys.platform.startswith('darwin')


def stem(path):
    """Returns the filename without path & extension."""
    return os.path.splitext(os.path.basename(path))[0]


# get_app_dir is from the Click package. Visit
# http://click.pocoo.org for more information on the click library.


def _posixify(name):
    """Coverts spaces to dashes; characters to lowercase."""
    return '-'.join(name.split()).lower()


def get_app_dir(app_name, roaming=True, force_posix=False):
    r"""Returns the config folder for the application.  The default behavior
    is to return whatever is most appropriate for the operating system.
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


def get_filename(config_path=None, roaming=True, force_posix=False):
    """Return the path/filename where the config will be stored.

    When config_path is a ...

        * PATH NAME: (looks like a directory)
            <config_path>/conf.toml

        * APP NAME (not a directory & doesn't have a file extension):
            <appdir>/<config_path>/conf.toml

        * FILE NAME (has a .toml extension):
            <config_path>

        * NOT SET:
            <appdir>/<progname>/conf.toml
    """

    # NOT SET
    if not config_path:
        path = get_app_dir(
            stem(sys.argv[0]), roaming=roaming, force_posix=force_posix
        )
        return os.path.join(path, 'conf.toml')

    # PATH NAME
    elif os.path.isdir(config_path):
        path = config_path
        return os.path.join(path, 'conf.toml')

    # APP NAME
    elif stem(config_path) == config_path:
        path = get_app_dir(
            config_path, roaming=roaming, force_posix=force_posix
        )
        return os.path.join(path, 'conf.toml')

    # FILE NAME
    elif os.path.basename(config_path).split('.')[1] == 'toml':
        return config_path

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
