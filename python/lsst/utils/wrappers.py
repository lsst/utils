from __future__ import absolute_import, division, print_function

import sys

__all__ = ("continueClass", "inClass", "TemplateMeta")


INTRINSIC_SPECIAL_ATTRIBUTES = frozenset((
    "__qualname__",
    "__module__",
    "__metaclass__",
    "__dict__",
    "__weakref__",
    "__class__",
    "__subclasshook__",
    "__name__",
))


def isAttributeSafeToTransfer(name, value):
    """Return True if an attribute is safe to monkeypatch-transfer to another
    class.

    This rejects special methods that are defined automatically for all
    classes, leaving only those explicitly defined in a class decorated by
    `continueClass` or registered with an instance of `TemplateMeta`.
    """
    if name.startswith("__"):
        if (value is not getattr(object, name, None) and
                name not in INTRINSIC_SPECIAL_ATTRIBUTES):
            return True
        else:
            return False
    return True


def continueClass(cls):
    """Re-open the decorated class, adding any new definitions into the original.

    For example,
    ::
        class Foo:
            pass

        @continueClass
        class Foo:
            def run(self):
                return None

    is equivalent to
    ::
        class Foo:
            def run(self):
                return None

    """
    orig = getattr(sys.modules[cls.__module__], cls.__name__)
    for name in dir(cls):
        # Common descriptors like classmethod and staticmethod can only be
        # accessed without invoking their magic if we use __dict__; if we use
        # getattr on those we'll get e.g. a bound method instance on the dummy
        # class rather than a classmethod instance we can put on the target
        # class.
        attr = cls.__dict__.get(name, None) or getattr(cls, name)
        if isAttributeSafeToTransfer(name, attr):
            setattr(orig, name, attr)
    return orig

