# A module that always works


def okay():
    return True


class Container:
    def inside():
        return "1"

    @classmethod
    def level(cls):
        import warnings

        from lsst.utils.introspection import find_outside_stacklevel

        stacklevel = find_outside_stacklevel("import_test")
        warnings.warn(f"Using stacklevel={stacklevel} in Container class", stacklevel=stacklevel)
        return stacklevel

    @classmethod
    def indirect_level(cls):
        return cls.level()
