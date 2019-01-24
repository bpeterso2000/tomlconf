r"""Get the config directory most appropriate for the platform.

get_app_dir is adapted from the Click package; http://click.pocoo.org
An app called ``"Foo Bar"`` would return something like the following:

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

from os import environ
from sys import platform, version_info

if version_info.major == 3 and version_info.minor >= 5:
    from pathlib import Path, PosixPath
else:
    from pathlib2 import Path, PosixPath

WIN = platform.startswith('win')
MAC = platform.startswith('darwin')


def get_app_dir(app_name, roaming=True, force_posix=False):
    if WIN:
        key = roaming and 'APPDATA' or 'LOCALAPPDATA'
        return Path(environ.get(key, Path.home())) / app_name
    if force_posix:
        return PosixPath('~/.' + app_name).expanduser()
    if MAC:
        return Path.expanduser('~/Library/Application Support') / app_name
    return PosixPath(
        environ.get('XDG_CONFIG_HOME', PosixPath('~/.config').expanduser())
    ) / app_name
