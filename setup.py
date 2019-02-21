from sys import version_info
from setuptools import setup, find_packages

PY2 = version_info.major == 2
PY3 = version_info.major == 3

install_requires = ['tomlkit>=0.5.3']
if PY2 or (PY3 and version_info.minor < 5):
    install_requires.append('pathlib2')

setup(
    name='tomlconf',
    version='0.3',
    url='http://github.com/bpeterso2000/tomlconf',
    author='Brian Peterson',
    author_email='bpeterso2000@yahoo.com',
    description='The tiny TOML configuration tool.',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=['pytest']
)
