import tomlkit.exceptions

import pytest

from tomlconf.container import TOMLDocument
from tomlconf.core import parse_toml
from tomlconf.errors import (
    TOMLConfError, TOMLKitError, TOMLParseError,
    KeyAlreadyPresent, NonExistentKey
)

parse_errors = [
    ('Unexpected character', tomlkit.exceptions.UnexpectedCharError),
    ('test = ["a", 1]', tomlkit.exceptions.MixedArrayTypesError),
    ('date = 2018-13-33', tomlkit.exceptions.InvalidDateError),
    ('time = 26:61:61', tomlkit.exceptions.InvalidTimeError),
    ('[]\ntest = 1', tomlkit.exceptions.EmptyTableNameError),
    (
        ' = [\n"in multiline arrays",\nLike here, \n"or here, and here"]',
        tomlkit.exceptions.EmptyKeyError
    ),
]


@pytest.fixture
def tomldoc():
    d = TOMLDocument()
    d['z'] = 'zulu'
    return d


@pytest.mark.parser
@pytest.mark.parametrize("data, tomlkit_error", parse_errors)
def test_parse_errors(data, tomlkit_error):
    for conf_err in (TOMLConfError, TOMLKitError, TOMLParseError):
        with pytest.raises(conf_err) as excinfo:
            parse_toml(data)
        assert isinstance(excinfo.value.__context__, tomlkit_error)
        assert excinfo.value.line
        assert excinfo.value.col


@pytest.mark.parser
def test_key_already_present():
    with pytest.raises(KeyAlreadyPresent):
        assert parse_toml('test = 1\ntest = 2')


@pytest.mark.container
def test_container_get(tomldoc):
    assert tomldoc['z'] == 'zulu'
    with pytest.raises(NonExistentKey):
        tomldoc['y']


@pytest.mark.container
def test_container_item(tomldoc):
    assert tomldoc.item('z') == 'zulu'
    with pytest.raises(NonExistentKey):
        tomldoc.item('y')


@pytest.mark.container
def test_container_set(tomldoc):
    tomldoc['x'] = 'factor'
    assert tomldoc['x'] == 'factor'
    tomldoc['x'] = 'refactor'
    assert tomldoc['x'] == 'refactor'


@pytest.mark.container
def test_container_add(tomldoc):
    tomldoc.add('x', 'factor')
    assert tomldoc['x'] == 'factor'
    with pytest.raises(KeyAlreadyPresent):
        tomldoc.add('x', 'factor')


@pytest.mark.container
def test_container_append(tomldoc):
    tomldoc.append('x', 'factor')
    assert tomldoc['x'] == 'factor'
    with pytest.raises(KeyAlreadyPresent):
        tomldoc.append('x', 'factor')


@pytest.mark.container
def test_container_del(tomldoc):
    assert tomldoc['z'] == 'zulu'
    del tomldoc['z']
    assert 'z' not in tomldoc
    with pytest.raises(NonExistentKey):
        del tomldoc['y']


@pytest.mark.container
def test_container_remove(tomldoc):
    assert tomldoc['z'] == 'zulu'
    tomldoc.remove('z')
    assert 'z' not in tomldoc
    with pytest.raises(NonExistentKey):
        tomldoc.remove('y')