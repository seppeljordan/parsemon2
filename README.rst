parsemon2
=========

This is yet another attempt to bring monadic parsing to python.  The
problem the author saw with many other implementations is a limit to
their composability.  A lot of the times these otherwise quite well
written implementations suffer pretty bad from pythons lack of TCO.
This implementation uses trampolines to get around that.

Right now this implementation is nothing more but a toy, but the tests
that come with this package show already that it's parsing ability is
not dependent on pythons recursion limit.

We also have error messages.

There is a (tested!) example implementation of a json parser included
in the package.  See ``src/parsemon/json.py`` for more information.

installation
============

This package should be available as a ``manylinux_2_24_x86_64`` wheel
on pypi.  On a update to date linux machine ``pip`` should do the job
just fine::

  pip install parsemon2

Currently MS Windows and macOS are not supported.

building the package
====================

Building the package from source can be done in multiple ways.

building from sdist
-------------------

You need to have the rust toolchain installed.  Check out your
GNU/Linux distribution to learn how to install it.  Another handy
resource to consider is `https://www.rust-lang.org/tools/install`.

Now you can build the package from source via ``pip``::

  pip install setuptools_rust wheel
  pip wheel parsemon2 --no-binary :all:

Now you should have a wheel for your platform in your working
directory.

build from the repository
-------------------------

The easiest way to build wheels from the git repository is to use
``docker`` since there is a handy build script included in the repo.
Make sure the your user has access to docker.  Consult the
documentation of your system for more information on how to install
docker.

With ``docker`` installed run the following in the root folder of the
source code repository::

  bin/build-wheels

After the program finishes you should find wheels for various python
versions in the ``dist/`` directory.


documentation
=============

If you want to learn about the library we recommend checking out our
`readthedocs page`_.


Changes
=======

3.2.2
=====

- Further performance improvements

3.2.1
-----

- Fixed minor bug in error handling code

3.2.0
-----

- Slight performance improvements
- Implement repeat combinator that tries to run a parser for a
  specified number of times

3.1.0
-----

- Serious peformance improvements were made
- Minor bug fix in json example parser

3.0.1
-----

- Update README

3.0
---

- Remove pyrsistent deque implementation
- Improve fmap performance
- Implement end-of-input parser
- ``run_parser`` now returns a ``ParsingResult`` object instead of the raw
  value of the supplied parser
- ``run_parser`` won't fail if the parser did not consume all of the
  supplied input
- Got rid of ``NotEnouhInput`` exception.
- Drop official support for Python 3.6
- Change semantics of ``until`` parser.

2.0
---

- Parsers constructed with ``do`` can now take arguments
- New parser for floating point numbers: ``parsmon.basic.floating_point``
- Implement ``x | y`` operator for parsers, it is a short hand for
  ``choice(x,y)``
- Improved performance parsing speed by factor 4 - 6
- There is now an example of a parser included in this package.  It is
  the worlds slowest json parser

1.1
---

- Implement validators
- ``chain`` now accepts 1 or more arguments
- Implement do notation
- New whitespace parser
- New parser for integers


.. _`readthedocs page`: https://parsemon2.readthedocs.io
