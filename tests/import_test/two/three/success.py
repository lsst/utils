# A module that always works


def okay() -> bool:
    """Return `True`."""
    return True


class Container:
    """Class for testing stacklevel."""

    def inside() -> int:
        """Return 1."""
        return "1"

    @classmethod
    def level(cls) -> int:
        """Return the stacklevel of the caller relative to this method."""
        import warnings

        from lsst.utils.introspection import find_outside_stacklevel

        stacklevel = find_outside_stacklevel("import_test")
        warnings.warn(f"Using stacklevel={stacklevel} in Container class", stacklevel=stacklevel)
        return stacklevel

    @classmethod
    def indirect_level(cls):
        """Return the stacklevel of the caller relative to this method.

        Deliberately includes an additional level.
        """
        return cls.level()
