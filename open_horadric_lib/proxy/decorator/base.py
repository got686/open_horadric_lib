from functools import wraps


def convenient_decorator(decorator):
    """
    Based on: http://stackoverflow.com/questions/653368
    """

    @wraps(decorator)
    def wrapped(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # Called as @decorator.
            return decorator(args[0])
        else:
            # Called as @decorator(*args, **kwargs).
            return lambda f: decorator(f, *args, **kwargs)

    return wrapped
