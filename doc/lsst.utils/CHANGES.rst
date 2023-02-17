lsst-utils v25.0.0 (2023-02-17)
===============================

New Features
------------

- Added ``lsst.utils.timer.profile`` to allow code blocks to be profiled easily. (`DM-35697 <https://jira.lsstcorp.org/browse/DM-35697>`_)


Miscellaneous Changes of Minor Interest
---------------------------------------

- Moved a module with a typing workaround for the built-in ``Ellipsis`` (``...``) singleton here, from ``daf_butler``. (`DM-36108 <https://jira.lsstcorp.org/browse/DM-36108>`_)
- Remove selected unit tests for memory reporting functions. (`DM-36960 <https://jira.lsstcorp.org/browse/DM-36960>`_)


lsst-utils v24.0.0 (2022-08-26)
===============================

New Features
------------

- Add option to ignore NaNs in ``lsst.utils.tests.assertFloatsAlmostEqual``. (`DM-29370 <https://jira.lsstcorp.org/browse/DM-29370>`_)
- Add test decorators to operate on cartesian product. (`DM-31141 <https://jira.lsstcorp.org/browse/DM-31141>`_)
- * Several new packages added from ``pipe_base`` and ``daf_butler``:

    * ``lsst.utils.timer``
    * ``lsst.utils.classes``
    * ``lsst.utils.introspection``
    * ``lsst.utils.iteration``
    * ``lsst.utils.logging``
  * Added ``lsst.utils.doImportType`` to import a python type from a string and guarantee it is not a module.
  * ``lsst.utils.get_caller_name`` is now deprecated in its current location and has been relocated to ``lsst.utils.introspection``. (`DM-31722 <https://jira.lsstcorp.org/browse/DM-31722>`_)
- Add `lsst.logging.set_trace_at` to control ``TRACE``-level loggers. (`DM-32142 <https://jira.lsstcorp.org/browse/DM-32142>`_)
- Builds using ``setuptools`` now calculate versions from the Git repository, including the use of alpha releases for those associated with weekly tags. (`DM-32408 <https://jira.lsstcorp.org/browse/DM-32408>`_)
- Context manager ``lsst.utils.timer.time_this`` can now include memory usage in its report. (`DM-33331 <https://jira.lsstcorp.org/browse/DM-33331>`_)
- A new package `lsst.utils.packages` has been added to allow system package versions to be obtained.
  This code has been relocated from ``lsst.base``. (`DM-33403 <https://jira.lsstcorp.org/browse/DM-33403>`_)
- Add ``lsst.utils.threads`` for control of threads.
  Use `lsst.utils.threads.disable_implicit_threading()` to disable implicit threading.
  This function should be used in place of ``lsst.base.disableImplicitThreading()`` in all new code.
  This package now depends on the `threadpoolctl` package. (`DM-33622 <https://jira.lsstcorp.org/browse/DM-33622>`_)
- Added a new class `lsst.utils.logging.PeriodicLogger` to allow a user to issue log messages after some time interval has elapsed. (`DM-33919 <https://jira.lsstcorp.org/browse/DM-33919>`_)
- Added ``lsst.utils.logging.getTraceLogger`` to simplify the creation of a trace logger that uses a ``TRACEn`` prefix for the logger name. (`DM-34208 <https://jira.lsstcorp.org/browse/DM-34208>`_)


API Changes
-----------

- The values for max resident set size stored in metadata are now consistently reported as bytes.
  Previously the units were platform specific (kibibytes on Liux and bytes on macOS). (`DM-20970 <https://jira.lsstcorp.org/browse/DM-20970>`_)
- ``deprecate_pybind11`` now requires a ``version`` parameter.
  This matches the upstream requirement from ``deprecated.deprecated`` (`DM-29701 <https://jira.lsstcorp.org/browse/DM-29701>`_)
- Add parameter to `~lsst.utils.packages.getEnvironmentPackages` to return all EUPS packages rather than just those that are locally setup. (`DM-33934 <https://jira.lsstcorp.org/browse/DM-33934>`_)


Performance Enhancement
-----------------------

- Fixed an optimization when using `lsst.utils.TemplateMeta` classes with `isinstance` or `issubclass`. (`DM-32661 <https://jira.lsstcorp.org/browse/DM-32661>`_)


lsst-utils v23.0.0 (2021-09-27)
===============================

- Moved all C++ code out of this package and into ``cpputils`` package and changed license to BSD 3-clause. (`DM-31721 <https://jira.lsstcorp.org/browse/DM-31721>`_)

lsst-utils v22.0 (2021-07-09)
=============================

Bug fix
-------

* Error reporting in `~lsst.utils.doImport` has been improved. [DM-27638]

lsst-utils v21.0 (2020-12-08)
=============================

New Features
------------

* Added a temporary directory context manager `lsst.utils.tests.temporaryDirectory`. [DM-26774]

API Change
----------

* Add an optional ``version`` parameter to `lsst.utils.deprecate_pybind11`. [DM-26285]
