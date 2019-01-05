import pytest
import os
import sys
import tempfile

import tomlkit

from tomlconf.core import Config, WIN, MAC, get_app_dir, get_filename

TOML_SAMPLE1 = """# This is a TOML document.
title = "TOML Example"
[owner]
name = "Tom Preston-Werner"
organization = "GitHub"
bio = "GitHub Cofounder & CEO\\nLikes tater tots and beer."
dob = 1979-05-27T07:32:00Z # First class dates? Why not?
[database]
server = "192.168.1.1"
ports = [8001, 8001, 8002]
connection_max = 5000
enabled = true
"""

TOML_SAMPLE2 = """
[table]
baz = 13
foo = "bar"
[table2]
array = [1, 2, 3]
"""

TOML_DOC = tomlkit.loads(TOML_SAMPLE1)
OLD_DATA = tomlkit.parse(TOML_SAMPLE1)
NEW_DATA = tomlkit.parse(TOML_SAMPLE2)
TOML_BLANK = tomlkit.document()

TEMP_PATH = tempfile.gettempdir()


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.toml')
    p.write(tomlkit.dumps(TOML_DOC))
    return str(p)


def test_read_only(tmpfile):
    with Config(tmpfile, 'r') as file:
        assert file.mode == 'r'
        assert file.data == OLD_DATA
        file.data = NEW_DATA
    with Config(tmpfile, 'r') as file:
        assert file.data == OLD_DATA


def test_write_only(tmpfile):
    with Config(tmpfile, 'w') as file:
        assert file.data == TOML_BLANK
        file.data = NEW_DATA
    with Config(tmpfile, 'r') as file:
        assert file.data == NEW_DATA


def test_read_write(tmpfile):
    with Config(tmpfile, 'r+') as file:
        assert file.data == OLD_DATA
        file.data = NEW_DATA
    with Config(tmpfile, 'r') as file:
        assert file.data == NEW_DATA


def test_invalid_mode(tmpfile):
    with pytest.raises(ValueError):
        with Config(tmpfile, 'w+'):
            pass


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
        with Config(tmpfile, 'r') as file:
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


@pytest.mark.getfile
def test_config_path_not_set():
    result = get_filename()
    progname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    endswith = os.path.join(progname, 'conf.toml')
    assert result.endswith(endswith)
    assert len(result) > len(endswith)


@pytest.mark.getfile
def test_config_path_is_path():
    assert get_filename(TEMP_PATH) == os.path.join(TEMP_PATH, 'conf.toml')


@pytest.mark.getfile
def test_config_path_looks_like_a_path():
    assert get_filename('/foo') == os.path.join('/foo', 'conf.toml')


@pytest.mark.getfile
def test_config_path_is_app_name():
    result = get_filename('foo')
    endswith = os.path.join(*os.path.split('foo/conf.toml'))
    assert result.endswith(endswith)
    assert len(result) > len(endswith)


@pytest.mark.getfile
def test_config_path_is_file_name():
    assert get_filename('foo.toml') == 'foo.toml'
    assert get_filename('/foo/bar.toml') == '/foo/bar.toml'


@pytest.mark.getfile
def test_config_path_is_file_with_bad_extension():
    with pytest.raises(ValueError):
        assert get_filename('/foo/bar.yaml')
    with pytest.raises(ValueError):
        assert get_filename('foo.yaml')
