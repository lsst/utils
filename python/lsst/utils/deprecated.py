import deprecated.sphinx
import functools


def deprecate_pybind11(func, reason, category=FutureWarning):
    """Deprecate a pybind11-wrapped C++ interface function or method.

    This needs to use a pass-through Python wrapper so that
    `~deprecated.sphinx.deprecated` can update its docstring; pybind11
    docstrings are native and cannot be modified.

    Note that this is not a decorator; its output must be assigned to
    replace the method being deprecated.

    Parameters
    ----------
    reason : `str`
        Reason for deprecation, passed to `~deprecated.sphinx.deprecated`
    category : `Warning`
        Warning category, passed to `~deprecated.sphinx.deprecated`

    Returns
    -------
    func : function
        Wrapped function

    Example
    -------
    ExposureF.getCalib = deprecate_pybind11(ExposureF.getCalib,
            reason="Replaced by getPhotoCalib. (Will be removed in 18.0)",
            category=FutureWarning))
    """
    @functools.wraps(func)
    def internal(*args, **kwargs):
        return func(*args, **kwargs)
    return deprecated.sphinx.deprecated(reason=reason, category=category)(internal)
