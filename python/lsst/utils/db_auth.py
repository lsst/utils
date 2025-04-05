# This file is part of utils.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import fnmatch
import json
import os
import stat
import urllib.parse

import yaml

__all__ = ["DbAuth", "DbAuthError", "DbAuthPermissionsError"]

_DEFAULT_PATH = "~/.lsst/db-auth.yaml"
_DEFAULT_ENVVAR = "LSST_DB_AUTH"
_DEFAULT_CREDS_ENVVAR = "LSST_DB_AUTH_CREDENTIALS"


class DbAuthError(RuntimeError):
    """Exception raised when a problem has occurred retrieving database
    authentication information.
    """

    pass


class DbAuthNotFoundError(DbAuthError):
    """Credentials file does not exist or no match was found in it."""


class DbAuthPermissionsError(DbAuthError):
    """Credentials file has incorrect permissions."""


class DbAuth:
    """Retrieves authentication information for database connections.

    The authorization configuration is taken from the ``authList`` parameter
    or a (group- and world-inaccessible) YAML file located at a path specified
    by the given environment variable or at a default path location.

    Parameters
    ----------
    path : `str` or `None`, optional
        Path to configuration file, default path is ``~/.lsst/db-auth.yaml``.
        The default is used if `None`.
    envVar : `str` or `None`, optional
        Name of environment variable pointing to configuration file, default is
        ``LSST_DB_AUTH``. This is used if the environment variable is available
        even if the path is specified. The default is used if `None`.
    authList : `list` [`dict`] or `None`, optional
        Authentication configuration. Used directly if given without referring
        to the environment.
    credsEnvVar : `str` or `None`, optional
        Name of environment variable containing the authentication
        configuration in JSON format. Default is ``LSST_DB_AUTH_CREDENTIALS``.
        If the environment variable is defined, this takes priority over
        reading credentials from file. The default is used if `None`.

    Notes
    -----
    Defaults will be used if no option is provided. If provided ``authList``
    will be used directly. The JSON credentials environment variable will
    be used if defined, in preference to reading from a file even if overrides
    are given for ``path`` and ``envVar``.
    """

    def __init__(
        self,
        path: str | None = _DEFAULT_PATH,
        envVar: str | None = _DEFAULT_ENVVAR,
        authList: list[dict[str, str]] | None = None,
        credsEnvVar: str | None = _DEFAULT_CREDS_ENVVAR,
    ):
        if authList is not None:
            self._db_auth_path = "<auth-list>"
            self.authList = authList
            return

        # Credentials in JSON takes priority.
        if jsonCreds := os.getenv(credsEnvVar or _DEFAULT_CREDS_ENVVAR):
            try:
                self.authList = json.loads(jsonCreds)
            except json.JSONDecodeError as exc:
                raise DbAuthError(
                    f"Unable to load DbAuth configuration using JSON environment variable {credsEnvVar}"
                ) from exc
            self._db_auth_path = "<json-env-var>"
            return

        secretPath = os.getenv(envVar or _DEFAULT_ENVVAR, path or _DEFAULT_PATH)
        secretPath = os.path.expanduser(secretPath)
        if not os.path.isfile(secretPath):
            raise DbAuthNotFoundError(f"No DbAuth configuration file: {secretPath}")
        mode = os.stat(secretPath).st_mode
        if mode & (stat.S_IRWXG | stat.S_IRWXO) != 0:
            raise DbAuthPermissionsError(
                f"DbAuth configuration file {secretPath} has incorrect permissions: {mode:o}"
            )

        try:
            with open(secretPath) as secretFile:
                self.authList = yaml.safe_load(secretFile)
        except Exception as exc:
            raise DbAuthError(f"Unable to load DbAuth configuration file: {secretPath}.") from exc
        self._db_auth_path = secretPath

    @property
    def db_auth_path(self) -> str:
        """The path to the secrets file used to load credentials (`str`)."""
        return self._db_auth_path

    # dialectname, host, and database are tagged as Optional only because other
    # routines delegate to this one in order to raise a consistent exception
    # for that condition.
    def getAuth(
        self,
        dialectname: str | None,
        username: str | None,
        host: str | None,
        port: int | str | None,
        database: str | None,
    ) -> tuple[str | None, str]:
        """Retrieve a username and password for a database connection.

        This function matches elements from the database connection URL with
        glob-like URL patterns in a list of configuration dictionaries.

        Parameters
        ----------
        dialectname : `str`
            Database dialect, for example sqlite, mysql, postgresql, oracle,
            or mssql.
        username : `str` or None
            Username from connection URL if present.
        host : `str`
            Host name from connection URL if present.
        port : `str` or `int` or None
            Port from connection URL if present.
        database : `str`
            Database name from connection URL.

        Returns
        -------
        username: `str`
            Username to use for database connection; same as parameter if
            present.
        password: `str`
            Password to use for database connection.

        Raises
        ------
        DbAuthError
            Raised if the input is missing elements, an authorization
            dictionary is missing elements, the authorization file is
            misconfigured, or no matching authorization is found.

        Notes
        -----
        The list of authorization configuration dictionaries is tested in
        order, with the first matching dictionary used.  Each dictionary must
        contain a ``url`` item with a pattern to match against the database
        connection URL and a ``password`` item.  If no username is provided in
        the database connection URL, the dictionary must also contain a
        ``username`` item.

        The ``url`` item must begin with a dialect and is not allowed to
        specify dialect+driver.

        Glob-style patterns (using "``*``" and "``?``" as wildcards) can be
        used to match the host and database name portions of the connection
        URL.  For the username, port, and database name portions, omitting them
        from the pattern matches against any value in the connection URL.

        Examples
        --------
        The connection URL
        ``postgresql://user@host.example.com:5432/my_database`` matches against
        the identical string as a pattern.  Other patterns that would match
        include:

        * ``postgresql://*``
        * ``postgresql://*.example.com``
        * ``postgresql://*.example.com/my_*``
        * ``postgresql://host.example.com/my_database``
        * ``postgresql://host.example.com:5432/my_database``
        * ``postgresql://user@host.example.com/my_database``

        Note that the connection URL
        ``postgresql://host.example.com/my_database`` would not match against
        the pattern ``postgresql://host.example.com:5432``, even if the default
        port for the connection is 5432.
        """
        # Check inputs, squashing MyPy warnings that they're unnecessary
        # (since they're only unnecessary if everyone else runs MyPy).
        if dialectname is None or dialectname == "":
            raise DbAuthError("Missing dialectname parameter")
        if host is None or host == "":
            raise DbAuthError("Missing host parameter")
        if database is None or database == "":
            raise DbAuthError("Missing database parameter")

        for authDict in self.authList:
            # Check for mandatory entries
            if "url" not in authDict:
                raise DbAuthError("Missing URL in DbAuth configuration")

            # Parse pseudo-URL from db-auth.yaml
            components = urllib.parse.urlparse(authDict["url"])

            # Check for same database backend type/dialect
            if components.scheme == "":
                raise DbAuthError("Missing database dialect in URL: " + authDict["url"])

            if "+" in components.scheme:
                raise DbAuthError(
                    "Authorization dictionary URLs should only specify "
                    f"dialects, got: {components.scheme}. instead."
                )

            # dialect and driver are allowed in db string, since functionality
            # could change. Connecting to a DB using different driver does not
            # change dbname/user/pass and other auth info so we ignore it.
            # https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
            dialect = dialectname.split("+")[0]
            if dialect != components.scheme:
                continue

            # Check for same database name
            if (
                components.path != ""
                and components.path != "/"
                and not fnmatch.fnmatch(database, components.path.lstrip("/"))
            ):
                continue

            # Check username
            if components.username is not None:
                if username is None or username == "":
                    continue
                if username != components.username:
                    continue

            # Check hostname
            if components.hostname is None:
                raise DbAuthError("Missing host in URL: " + authDict["url"])
            if not fnmatch.fnmatch(host, components.hostname):
                continue

            # Check port
            if components.port is not None and (port is None or str(port) != str(components.port)):
                continue

            # Don't override username from connection string
            if username is not None and username != "":
                return (username, authDict["password"])
            else:
                if "username" not in authDict:
                    return (None, authDict["password"])
                return (authDict["username"], authDict["password"])

        raise DbAuthNotFoundError(
            f"No matching DbAuth configuration for: ({dialectname}, {username}, {host}, {port}, {database})"
        )

    def getUrl(self, url: str) -> str:
        """Fill in a username and password in a database connection URL.

        This function parses the URL and calls `getAuth`.

        Parameters
        ----------
        url : `str`
            Database connection URL.

        Returns
        -------
        url : `str`
            Database connection URL with username and password.

        Raises
        ------
        DbAuthError
            Raised if the input is missing elements, an authorization
            dictionary is missing elements, the authorization file is
            misconfigured, or no matching authorization is found.

        See Also
        --------
        getAuth : Retrieve authentication credentials.
        """
        components = urllib.parse.urlparse(url)
        username, password = self.getAuth(
            components.scheme,
            components.username,
            components.hostname,
            components.port,
            components.path.lstrip("/"),
        )
        hostname = components.hostname
        assert hostname is not None
        if ":" in hostname:  # ipv6
            hostname = f"[{hostname}]"
        assert username is not None
        netloc = "{}:{}@{}".format(
            urllib.parse.quote(username, safe=""), urllib.parse.quote(password, safe=""), hostname
        )
        if components.port is not None:
            netloc += ":" + str(components.port)
        return urllib.parse.urlunparse(
            (
                components.scheme,
                netloc,
                components.path,
                components.params,
                components.query,
                components.fragment,
            )
        )
