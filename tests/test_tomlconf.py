import pytest
import os
import sys

from tomlconf import Config, WIN, get_app_dir


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.txt')
    p.write('test data')
    return str(p)


def test_read_only(tmpfile):
    with Config(tmpfile, 'r') as file:
        assert file.mode == 'r'
        assert file.data == 'test data'
        file.data = 'new data'
    with Config(tmpfile, 'r') as file:
        assert file.data == 'test data'


def test_write_only(tmpfile):
    with Config(tmpfile, 'w') as file:
        assert file.data == ''
        file.data = 'new data'
    with Config(tmpfile, 'r') as file:
        assert file.data == 'new data'


def test_read_write(tmpfile):
    with Config(tmpfile, 'r+') as file:
        assert file.data == 'test data'
        file.data = 'new data'
    with Config(tmpfile, 'r') as file:
        assert file.data == 'new data'


def test_invalid_mode(tmpfile):
    with pytest.raises(ValueError):
        with Config(tmpfile, 'w+'):
            pass


def test_encoding(tmpfile):
    with Config(tmpfile, 'w', encoding='iso-8859-5') as file:
        file.data = 'test data: данные испытани'
    with pytest.raises(UnicodeDecodeError):
        with Config(tmpfile, 'r') as file:
            pass
    with Config(tmpfile, 'r', encoding='utf-8', errors='replace') as file:
        assert file.data == 'test data: ������ ��������'
    with Config(tmpfile, 'r', encoding='iso-8859-5') as file:
        assert file.data == 'test data: данные испытани'


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
@pytest.mark.skipif(not sys.platform == 'darwin', reason='For Mac OS X Platform Only')
def test_get_mac_app_dir():
    app_dir = os.path.join(os.path.expanduser('~'), '/Library/Application Support')
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'Foo Bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN, reason="Only for non Windows based systems")
def test_get_posix_app_dir():
    app_dir = os.path.expanduser('~')
    result = get_app_dir('Foo Bar', force_posix=True)
    assert app_dir in result and '.foo-bar' in result


@pytest.mark.appdir
@pytest.mark.skipif(WIN or sys.platform == 'darwin', reason="Only for non Windows based systems")
def test_get_nix_app_dir():
    app_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    result = get_app_dir('Foo Bar')
    assert app_dir in result and 'foo-bar' in result
