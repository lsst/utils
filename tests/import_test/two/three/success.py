# A module that always works


def okay() -> bool:
    """Return `True`."""
    return True


class Container:
    """Class for testing stacklevel."""

    def inside() -> str:
        """Return 1."""
        return "1"

    @classmethod
    def level(cls, allow_methods=frozenset(), allow_modules=frozenset()) -> int:
        """Return the stacklevel of the caller relative to this method."""
        import warnings

        from lsst.utils.introspection import find_outside_stacklevel

        stacklevel = find_outside_stacklevel(
            "import_test", allow_methods=allow_methods, allow_modules=allow_modules
        )
        warnings.warn(f"Using stacklevel={stacklevel} in Container class", stacklevel=stacklevel)
        return stacklevel

    @classmethod
    def indirect_level(cls, allow_methods=frozenset(), allow_modules=frozenset()):
        """Return the stacklevel of the caller relative to this method.

        Deliberately includes an additional level.
        """
        return cls.level(allow_methods=allow_methods, allow_modules=allow_modules)
