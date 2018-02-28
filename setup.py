from distutils.core import setup

setup(
    name='parsemon2',
    description=u"A monadic parser combinator written purely in python",
    package_dir = {'': 'src'},
    version="1.0",
    license="GPL-3",
    packages=['parsemon']
)
