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
    packages=['parsemon'],
    install_requires=[
        'attrs'
    ],
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
