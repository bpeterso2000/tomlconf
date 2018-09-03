import os
import sys


class File:
    """File context manager

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

    """This section of code taken from the Click module instead of bring in the entire
    library for this one function.
    Please visit http://click.pocoo.org for more information on the click library

    The comment END CLICK CODE below marks the end of the click library code 
    """
    _WIN = sys.platform.startswith('win')
    """***********************************************
                       END CLICK CODE
    ***********************************************"""

    def __init__(self, filename, mode='r', encoding='utf-8', errors='strict'):
        if mode not in ('r', 'r+', 'w'):
            raise ValueError(
              "File context manager mode must be 'r', 'r+' or 'w'."
            )
        self.__openfile = None
        self._mode = mode
        self.filename = filename
        self.path = self._get_app_dir(
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
        print(self.path)
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

    """This section of code taken from the Click module instead of bring in the entire
    library for this one function.
    Please visit http://click.pocoo.org for more information on the click library

    The comment END CLICK CODE below marks the end of the click library code 
    """
    @staticmethod  # @staticmethod added by Archie White for the tomlconf project
    def _posixify(name):
        return '-'.join(name.split()).lower()

    def _get_app_dir(self, app_name, roaming=True, force_posix=False):
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

        .. versionadded:: 2.0

        :param app_name: the application name.  This should be properly capitalized
                         and can contain whitespace.
        :param roaming: controls if the folder should be roaming or not on Windows.
                        Has no affect otherwise.
        :param force_posix: if this is set to `True` then on any POSIX system the
                            folder will be stored in the home folder with a leading
                            dot instead of the XDG config home or darwin's
                            application support folder.
        """
        if self._WIN:
            key = roaming and 'APPDATA' or 'LOCALAPPDATA'
            folder = os.environ.get(key)
            if folder is None:
                folder = os.path.expanduser('~')
            return os.path.join(folder, app_name)
        if force_posix:
            return os.path.join(os.path.expanduser('~/.' + self._posixify(app_name)))
        if sys.platform == 'darwin':
            return os.path.join(os.path.expanduser(
                '~/Library/Application Support'), app_name)
        return os.path.join(
            os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
            self._posixify(app_name))

    """***********************************************
                       END CLICK CODE
    ***********************************************"""


if __name__ == "__main__":
    with File('aewhite.txt', mode='w') as f:
        f.text = 'This is a test'
