import tomlconf as tc
from pathlib import Path
import pytest


def test_file_create_write_w(tmpdir):
    p = tmpdir.mkdir('sub').join('test_w.txt')
    file_name = str(p)
    assert not Path(file_name).is_file()  # file does not exist
    with tc.File(file_name, 'w') as my_file:
        assert Path(file_name).is_file()  # file does exist
        assert my_file.text == ''  # nothing in text
        my_file.text = 'Content'
    assert p.read() == 'Content'  # my_file.text was written


def test_file_open_write_w(tmpdir):
    p = tmpdir.mkdir('sub').join('test_w.txt')
    file_name = str(p)
    with tc.File(file_name, 'w') as my_file:
        my_file.text = 'archie'  # this should get over written in the test
    assert p.read() == 'archie'  # maker sure the test data is there
    with tc.File(file_name, 'w') as my_file:
        assert my_file.text == ''  # we should not have read anything in
        my_file.text = 'Content'
    assert p.read() == 'Content'  # The file should now only contain 'Content'


def test_file_open_r(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
        my_file.text = 'Not the Content'
    assert p.read() == 'Content'  # nope, we did not write the changes back


def test_file_open_rp_longer(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r+') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r+') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
        my_file.text += '. And some more content'
    assert p.read() == 'Content. And some more content'  # yep, the file contents equals the result of our changes


def test_file_open_rp_shorter(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r+') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r+') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
        my_file.text = 'This'
    assert p.read() == 'This'  # yep, the file contents equals the result of our changes


def test_file_open_rp_same(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r+') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r+') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
    assert p.read() == 'Content'  # yep, the file contents equals the result of our changes


def test_file_open_rp_empty(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r+') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r+') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
        my_file.text = ''
    assert p.read() == ''  # yep, the file contents equals the result of our changes


def test_file_open_rp_none(tmpdir):
    p = tmpdir.mkdir('sub').join('test.txt')
    file_name = str(p)
    with pytest.raises(FileNotFoundError):  # nope we did not create the file
        with tc.File(file_name, 'r+') as my_file:
            pass
    p.write('Content')  # put something out there to read
    with tc.File(file_name, 'r+') as my_file:
        assert my_file.text == 'Content'  # yep we read in the file
        my_file.text = None
    assert p.read() == 'None'  # yep, the file contents equals the result of our changes


def test_bad_mode():
    with pytest.raises(ValueError):
        with tc.File('test.txt', 'w+') as my_file:
            pass


def test_encoding(tmpfile):
    with tc.File(tmpfile, 'w', encoding='iso-8859-5') as file:
        file.text = 'test data: данные испытани'
    with pytest.raises(UnicodeDecodeError):
        with tc.File(tmpfile, 'r') as file:
            pass
    with tc.File(tmpfile, 'r', encoding='utf-8', errors='replace') as file:
        assert file.text == 'test data: ������ ��������'
    with tc.File(tmpfile, 'r', encoding='iso-8859-5') as file:
        assert file.text == 'test data: данные испытани'
