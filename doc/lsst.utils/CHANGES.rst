lsst.utils v22.0 (2021-07-09)
=============================

Bug fix
-------

* Error reporting in `~lsst.utils.doImport` has been improved. [DM-27638]

lsst.utils v21.0 (2020-12-08)
=============================

New Features
------------

* Added a temporary directory context manager `lsst.utils.tests.temporaryDirectory`. [DM-26774]

API Change
----------

* Add an optional ``version`` parameter to `lsst.utils.deprecate_pybind11`. [DM-26285]
