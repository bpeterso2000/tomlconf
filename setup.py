from setuptools import setup, find_packages

setup(
    name='tomlconf',
    version='0.1',
    url='http://github.com/bpeterso2000/tomlconf',
    author='Name',
    author_email='author@mail.com',
    description='Description of my package',
    packages=find_packages(), install_requires=['tomlkit']
)
