try:
    # For now, ensure that backtrace has been imported if somebody
    # is relying on it from a lsst.utils import. Treat it as an optional
    # import.
    import lsst.cpputils.backtrace
except ImportError:
    pass

from .._forwarded import isEnabled
