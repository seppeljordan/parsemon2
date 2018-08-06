from .coroutine import do
from .parser import many, one_of


@do
def integer():
    first = yield one_of('+-0123456789')
    if first == '-':
        sign = -1
        first = yield one_of('0123456789')
    elif first == '+':
        sign = 1
        first = yield one_of('0123456789')
    else:
        sign = 1
    rest = yield many(one_of('0123456789'))
    return sign * int(first + ''.join(rest))
