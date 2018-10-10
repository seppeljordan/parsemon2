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

1.1
---

- Implement validators
- ``chain`` now accepts 1 or more arguments
- Implement do notation
- New whitespace parser
- New parser for integers
