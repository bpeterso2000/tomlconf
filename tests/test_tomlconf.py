import pytest

from tomlconf import File


@pytest.fixture
def tmpfile(tmpdir):
    p = tmpdir.mkdir('testdir').join('testfile.txt')
    p.write('test data')
    return str(p)


def test_read_only(tmpfile):
    with File(tmpfile, 'r') as file:
        assert file.mode == 'r'
        assert file.text == 'test data'
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'test data'


def test_write_only(tmpfile):
    with File(tmpfile, 'w') as file:
        assert file.text == ''
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'new data'


def test_read_write(tmpfile):
    with File(tmpfile, 'r+') as file:
        assert file.text == 'test data'
        file.text = 'new data'
    with File(tmpfile, 'r') as file:
        assert file.text == 'new data'


def test_invalid_mode(tmpfile):
    with pytest.raises(ValueError):
        with File(tmpfile, 'w+'):
            pass

def test_encoding(tmpfile):
    with File(tmpfile, 'w', encoding='iso-8859-5') as file:
        file.text = 'test data: данные испытани'
    with pytest.raises(UnicodeDecodeError):
        with File(tmpfile, 'r') as file:
            pass
    with File(tmpfile, 'r', encoding='utf-8', errors='replace') as file:
        assert file.text == 'test data: ������ ��������'
    with File(tmpfile, 'r', encoding='iso-8859-5') as file:
        assert file.text == 'test data: данные испытани'
