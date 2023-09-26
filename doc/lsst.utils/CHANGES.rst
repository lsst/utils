lsst-utils v26.0.0 (2023-09-22)
===============================

This release no longer works with Python 3.8.

New Features
------------

- Now works with Python 3.11.
  Python 3.11 now ensures that the ``stacklevel`` parameter for logging methods is now consistent independent of how many method calls are involved internally. (`DM-37987 <https://jira.lsstcorp.org/browse/DM-37987>`_)
- Added ``lsst.utils.tests.ImportTestCase`` class.
  This test case can be used to force the import of every file in a package.
  This can be very useful for spotting obvious problems if a package does not export every file by default. (`DM-35901 <https://jira.lsstcorp.org/browse/DM-35901>`_)
- Added a utility function, ``calculate_safe_plotting_limits``, located in ``lsst.utils.plotting.limits``, for calculating plotting limits for data with large outliers. (`DM-38386 <https://jira.lsstcorp.org/browse/DM-38386>`_)
- ``MemoryTestCase`` now can accept an "ignore" list of regexps that match acceptable open files. (`DM-38764 <https://jira.lsstcorp.org/browse/DM-38764>`_)
- Adds an alternative way of interacting with ``calculate_safe_plotting_limits()``.

  This change adds a factory interface, such that one can use the function to accumulate the safe plotting limits over many different data series without having them all in-hand, by using the ``make_calculate_safe_plotting_limits()`` function to return a ``calculate_safe_plotting_limits()`` which will return the common limits after the addition of each new data series. The original behaviour remains unchanged. (`DM-38900 <https://jira.lsstcorp.org/browse/DM-38900>`_)
- Added ``lsst.utils.introspection.find_outside_stacklevel``.
  This function can be used to calculate the stack level that should be passed to warnings and log messages in order to make them look like they came from the line outside the specified package in user code. (`DM-39628 <https://jira.lsstcorp.org/browse/DM-39628>`_)
- Update the interface to ``lsst.utils.introspection.find_outside_stacklevel`` to allow multiple modules to be skipped in the hierarchy and also specify that some methods and modules should not be skipped. (`DM-40032 <https://jira.lsstcorp.org/browse/DM-40032>`_)
- Added the ability for ``find_outside_stacklevel`` to return additional information about the matching stack to the caller.
  This allows, for example, the filename and lineno to be reported without the caller making another call to ``inspect.stack()`` or calling ``get_caller_name``. (`DM-40367 <https://jira.lsstcorp.org/browse/DM-40367>`_)
- Added the ``lsst.utils.db_auth.DbAuth`` class that has been relocated from ``daf_butler``. (`DM-40462 <https://jira.lsstcorp.org/browse/DM-40462>`_)


Bug Fixes
---------

- Fixed ``time_this`` when ``mem_usage=True`` to prevent memory statistics being gathered when the log message would not be issued.
  We had been trapping this on the exit to the context manager but not entry for the initial memory statistics gathering. (`DM-38587 <https://jira.lsstcorp.org/browse/DM-38587>`_)
- Updated the python version handling such that it is no longer a failure for the python package version to disagree with the ``.version`` property of that package.
  The package version is now used in preference if there is a disagreement. (`DM-38665 <https://jira.lsstcorp.org/browse/DM-38665>`_)


Miscellaneous Changes of Minor Interest
---------------------------------------

- Modified the code that determines the versions of Python packages so that it now uses `importlib.metadata`.
  This is slightly slower than accessing ``__version__`` but does give more consistent results. (`DM-38812 <https://jira.lsstcorp.org/browse/DM-38812>`_)
- Improved the performance of ``lsst.utils.packages.getPythonPackages()`` to use the namespace hierarchy so it now only needs to check as deep into the hierarchy as is needed to find a version.
  Additionally, the code no longer tries to extract versions from Python standard library packages. (`DM-39402 <https://jira.lsstcorp.org/browse/DM-39402>`_)


An API Removal or Deprecation
-----------------------------

- Dropped support for Python 3.8. (`DM-35901 <https://jira.lsstcorp.org/browse/DM-35901>`_)
- * Removed deprecated APIs from `lsst.utils.logging`.
  * Removed deprecated ``demangleType`` and ``backtrace`` that were forwarded from ``cpputils``.
  * Removed ``cpputils`` from the EUPS table file. (`DM-37534 <https://jira.lsstcorp.org/browse/DM-37534>`_)
- A Mypy workaround in the ``ellipsis`` module is not needed for Python 3.10 or newer.
  Importing ``lsst.utils.ellipsis`` in these Python versions will produce a `DeprecationWarning`. (`DM-39410 <https://jira.lsstcorp.org/browse/DM-39410>`_)
- Removed deprecated ``lsst.utils.get_caller_name``. Use ``lsst.utils.introspection``. (`DM-40032 <https://jira.lsstcorp.org/browse/DM-40032>`_)


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
- Add `lsst.utils.logging.trace_set_at` to control ``TRACE``-level loggers. (`DM-32142 <https://jira.lsstcorp.org/browse/DM-32142>`_)
- Builds using ``setuptools`` now calculate versions from the Git repository, including the use of alpha releases for those associated with weekly tags. (`DM-32408 <https://jira.lsstcorp.org/browse/DM-32408>`_)
- Context manager ``lsst.utils.timer.time_this`` can now include memory usage in its report. (`DM-33331 <https://jira.lsstcorp.org/browse/DM-33331>`_)
- A new package ``lsst.utils.packages`` has been added to allow system package versions to be obtained.
  This code has been relocated from ``lsst.base``. (`DM-33403 <https://jira.lsstcorp.org/browse/DM-33403>`_)
- Add ``lsst.utils.threads`` for control of threads.
  Use `lsst.utils.threads.disable_implicit_threading()` to disable implicit threading.
  This function should be used in place of ``lsst.base.disableImplicitThreading()`` in all new code.
  This package now depends on the ``threadpoolctl`` package. (`DM-33622 <https://jira.lsstcorp.org/browse/DM-33622>`_)
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
