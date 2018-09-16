import os
import sys
import tomlkit

def _posixify(name):
    return '-'.join(name.split()).lower()


def get_app_dir(app_name, roaming=True, force_posix=False):
    r"""Returns the config folder for the application.  The default
    behavior is to return whatever is most appropriate for the operating
    system.

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
    if sys.platform.startswith('win'):
        key = roaming and 'APPDATA' or 'LOCALAPPDATA'
        folder = os.environ.get(key, os.path.expanduser('~'))
        return os.path.join(folder, app_name)

    if force_posix:
        return os.path.join(
            os.path.expanduser('~/.' + _posixify(app_name))
        )

    if sys.platform == 'darwin':
        # Mac OS X
        return os.path.join(
            os.path.expanduser('~/Library/Application Support'),
            app_name
        )

    return os.path.join(
        os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
        _posixify(app_name)
    )


class Config:
    """File context manager for TOML config file

    filename (str):
        file path/name
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

    def __init__(self, filename, mode='r', encoding='utf-8', errors='strict'):
        if mode not in ('r', 'r+', 'w'):
            raise ValueError(
              "File context manager mode must be 'r', 'r+' or 'w'."
            )
        self.__openfile = None
        self._mode = mode
        self.filename = filename
        self.path = get_app_dir(
            os.path.splitext(
                os.path.split(
                    sys.argv[0]
                    )[1]
                )[0]
            )
        self.encoding = encoding
        self.errors = errors
        self.text = ''

    @property
    def mode(self):
        return self._mode

    def __enter__(self):
        print(self.path, file=sys.stderr)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.__openfile = open(
            os.path.join(self.path, self.filename),
            mode=self.mode,
            encoding=self.encoding,
            errors=self.errors,
            newline=''
        )
        if 'r' in self.mode:
            self.text = self.__openfile.read()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__openfile:
            if self.mode in ('r+', 'w'):
                self.__openfile.seek(0)
                self.__openfile.write(str(self.text))
                self.__openfile.truncate()
            self.__openfile.close()
