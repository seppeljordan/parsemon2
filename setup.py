from distutils.core import setup

with open('VERSION') as f:
    VERSION=f.readlines()[0]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='parsemon2',
    version=VERSION,
    author='Sebastian Jordan',
    author_email='sebastian.jordan.mail@googlemail.com',
    long_description=long_description,
    description=u"A monadic parser combinator written purely in python",
    package_dir = {'': 'src'},
    license="GPL-3",
    packages=['parsemon'],
    install_requires=[
        'attrs'
    ],
)
