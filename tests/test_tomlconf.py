import pytest
import os
import sys
import tomlkit


from tomlconf.core import Config, WIN, MAC, get_app_dir, get_filename, stem

file_content = """# This is a TOML document.
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

old_data = tomlkit.parse(file_content)

file_content_2 = """
[table]
baz = 13
foo = "bar"
[table2]
array = [1, 2, 3]
"""

new_data = tomlkit.parse(file_content_2)
toml_doc = tomlkit.loads(file_content)
toml_blank = tomlkit.document()

get_filename_params = [
    ('', True, False),
    ('', False, True),
    ('', True, True),
    ('', False, False),
    ('/Users/archiewhite', True, False),
    ('/Users/archiewhite', False, True),
    ('/Users/archiewhite', True, True),
    ('/Users/archiewhite', False, False),
    ('fubar', True, False),
    ('fubar', False, True),
    ('fubar', True, True),
    ('fubar', False, False),
    ('/hello/bob.toml', True, False),
    ('/hello/bob.toml', False, True),
    ('/hello/bob.toml', True, True),
    ('/hello/bob.toml', False, False),
]


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.toml')
    p.write(tomlkit.dumps(toml_doc))
    return str(p)


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


@pytest.mark.get_filename
@pytest.mark.parametrize('config_path, roaming, force_posix', get_filename_params)
def test_get_filename(config_path, roaming, force_posix):
    result = get_filename(config_path, roaming, force_posix)
    if not config_path:
        # Scenario 1
        assert result == os.path.join(get_app_dir(stem(sys.argv[0]), roaming=roaming, force_posix=force_posix),
                                      'conf.toml')
    elif os.path.isdir(config_path):
        # Scenario 2
        assert result == os.path.join(config_path, 'conf.toml')
    elif stem(config_path) == config_path:
        # Scenario 3
        assert result == os.path.join(get_app_dir(config_path, roaming=roaming, force_posix=force_posix), 'conf.toml')
    elif os.path.basename(config_path).split('.')[1] == 'toml':
        # Scenario 4
        assert result == config_path