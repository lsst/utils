# This will fail to import because of ModuleNotFoundError
import notthere


def myfunc():
    """Return a module that can not be imported."""
    return notthere
