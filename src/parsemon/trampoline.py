from functools import wraps


class Result(object):
    def __init__(self, value):
        self.value = value

    def is_result(self):
        return True

    def __call__(self):
        return self.value


class Call(object):
    def __init__(self, f, *args, **kwargs):
        self.fun = f
        self.args = args
        self.kwargs = kwargs

    def is_result(self):
        return False

    def __call__(self):
        return self.fun(*(self.args), **(self.kwargs))

def with_trampoline(f):
    @wraps(f)
    def g(*args,**kwargs):
        iteration_result = f(*args,**kwargs)
        while True:
            if iteration_result.is_result():
                return iteration_result()
            else:
                iteration_result = iteration_result()
    return g
