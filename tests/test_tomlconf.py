import os

import pytest
import tomlkit
import tomlkit.exceptions

import tomlconf
from tomlconf import Config, WIN, MAC, get_app_dir, TomlConfError, ModeError

file_content = """# This is a TOML document.

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
organization = "GitHub"
bio = "GitHub Cofounder & CEO Likes tater tots and beer."
dob = 1979-05-27T07:32:00Z # First class dates? Why not?

[database]
server = "192.168.1.1"
ports = [8001, 8001, 8002]
connection_max = 5000
enabled = true
"""

bad_file_content = """# This is a TOML document.

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
name = "Tom Preston-Werner"
organization = "GitHub"
bio = "GitHub Cofounder & CEO Likes tater tots and beer."
dob = 1979-05-27T07:32:00Z # First class dates? Why not?

[database]
server = "192.168.1.1"
ports = [8001, 8001, 8002]
connection_max = 5000
enabled = true
"""

DOUBLE_KEY = """# TOML with double key error

title = "TOML Excample"

[owner]
name = "Archie"
name = "Ernest"
"""

old_data = tomlkit.parse(file_content)

file_content_2 = """
[table]
baz = 13
foo = "bar"

[table2]
array = [1, 2, 3]
"""

file_content_3 = """
[table]
baz = 13
foo = "bar"

[table2]
array = [1, 2, 3]
"""

new_data = tomlkit.parse(file_content_2)

toml_doc = tomlkit.loads(file_content)

toml_blank = tomlkit.document()


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.txt')
    p.write(tomlkit.dumps(toml_doc))
    return str(p)


@pytest.fixture
def tmpfile_bad(tmpdir):
    def _foo(data_string):
        p = tmpdir.mkdir('testdir').join('testfile.txt')
        p.write(data_string)
        return str(p)
    return _foo


def test_read_only(tmpfile):
    with Config(tmpfile, 'r') as file:
        assert file.mode == 'r'
        assert file.data == old_data
        file.data = new_data
    with Config(tmpfile, 'r') as file:
        assert file.data == old_data


def test_write_only(tmpfile):
    with Config(tmpfile, 'w') as file:
        assert file.data == toml_blank
        file.data = new_data
    with Config(tmpfile, 'r') as file:
        assert file.data == new_data


def test_read_write(tmpfile):
    with Config(tmpfile, 'r+') as file:
        assert file.data == old_data
        file.data = new_data
    with Config(tmpfile, 'r') as file:
        assert file.data == new_data


def test_invalid_mode(tmpfile):
    with pytest.raises(ModeError):
        with Config(tmpfile, 'w+'):
            pass


def test_tomlconferror(tmpfile):
    try:
        with Config(tmpfile, 'q'):
            pass
    except TomlConfError as e:
        assert str(e) == 'File mode must be "r", "r+" or "w" not %s' % '"q"'


def test_encoding(tmpfile):
    test_data_iso_8859_5 = tomlkit.loads("""
        [entry]
        testdata = "данные испытани"
    """)
    test_data_utf_8 = tomlkit.loads("""
        [entry]
        testdata = "������ ��������"
    """)
    with Config(tmpfile, 'w', encoding='iso-8859-5') as file:
        file.data = test_data_iso_8859_5
    with pytest.raises(UnicodeDecodeError):
        with Config(tmpfile, 'r'):
            pass
    with Config(tmpfile, 'r', encoding='utf-8', errors='replace') as file:
        assert file.data == test_data_utf_8
    with Config(tmpfile, 'r', encoding='iso-8859-5') as file:
        assert file.data == test_data_iso_8859_5


@pytest.mark.appdir
@pytest.mark.skipif(not WIN, reason='For Windows platforms only')
def test_get_win_app_dir():
    app_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    result = get_app_dir('Foo Bar', roaming=False)
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(not WIN, reason='For Windows platforms only')
def test_get_win_app_dir_roaming():
    app_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
    result = get_app_dir('Foo Bar', roaming=True)
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(not MAC, reason='For Mac OS X Platform Only')
def test_get_mac_app_dir():
    app_dir = os.path.join(
        os.path.expanduser('~'),
        '/Library/Application Support'
    )
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN, reason="Only for non Windows based systems")
def test_get_posix_app_dir():
    app_dir = os.path.expanduser('~')
    result = get_app_dir('Foo Bar', force_posix=True)
    assert app_dir in result and '.foo-bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN or MAC, reason="Only for non Windows based systems")
def test_get_nix_app_dir():
    app_dir = os.environ.get(
        'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
    )
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'foo-bar' in result


def test_TomlConfError(tmpfile_bad):
    try:
        with Config(tmpfile_bad(DOUBLE_KEY), 'r'):
            pass
    except tomlconf.TomlConfError as e:
        assert str(e) == 'Key "name" already exists.'


# def test_FileError(tmpfile_bad):
#     try:
#         with Config('filedoesnotexist.txt', 'r'):
#             pass
#     except tomlconf.FileError as e:
#         assert str(e) == "[Errno 2] No such file or directory: ' '"


def test_KeyAlreadyPresent(tmpfile_bad):
    try:
        with Config(tmpfile_bad(DOUBLE_KEY), 'r'):
            pass
    except tomlconf.KeyAlreadyPresent as e:
        assert str(e) == 'Key "name" already exists.'
