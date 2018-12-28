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


Changes
=======

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
