from __future__ import unicode_literals, print_function

import os
import sys
import logging
import json
from decimal import Decimal, InvalidOperation
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

try:
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    class ImproperlyConfigured(Exception):
        """Configuration Exception

        Imported from Django if available, otherwise defined as
        a simple subclass of Exception
        """
        pass

try:
    from django.utils.six import string_types
except ImportError:
    if sys.version_info[0] == 3:
        string_types = (str,)
        text_type = str
    else:
        string_types = (basestring,)
        text_type = unicode


__version__ = '0.1.1'


NOTSET = type(str('NoValue'), (object,), {})


logger = logging.getLogger(__name__)


class Environment(object):
    """Class for reading and casting environment variables

    This class presents the main interface for interacting with the
    environment. Once instantiated, it can either be called as a function,
    or any of the convenience methods can be used.

    Args:
        environ (`dict`): Environment to read variables from
    """

    _collections = (dict, list, set, tuple)
    _lists = (list, set, tuple)

    def __init__(self, environ):
        self.environ = environ

    def __call__(self, var, default=NOTSET, cast=None, force=True):
        """Function interface

        Once the environment has been initialised, it can be called as a
        function. This is necessary to provide custom casting, or it can
        sometimes be preferred for consistency.

        Examples:
            Casting an environment variable:

            >>> env = Environment({'MY_VAR': '1'})
            >>> env('MY_VAR', cast=int)
            1

            Providing a default:

            >>> env = Environment({})
            >>> env('ANOTHER_VAR', default='value')
            "value"

        Args:
            var (`str`): The name of the environment variable
            default: The value to return if the environment variable does not
                exist
            cast: type or function for casting environment variable. See
                casting
            force (`bool`): Whether to force casting of the default value

        Returns:
            The environment variable if it exists, otherwise default

        Raises:
            ImproperlyConfigured
        """
        return self._get(var, default=default, cast=cast, force=force)

    def __contains__(self, var):
        """Test if an environment variable exists

        Allows using the ``in`` operator to test if an environment variable
        exists.

        Examples:
            >>> env = Environment({'MY_VAR': '1'})
            >>> 'MY_VAR' in env
            True
            >>> 'ANOTHER_VAR' in env
            False
        """
        return var in self.environ

    # Simple builtins

    def bool(self, var, default=NOTSET, force=True):
        """Convenience method for casting to a bool"""
        return self._get(var, default=default, cast=bool, force=force)

    def float(self, var, default=NOTSET, force=True):
        """Convenience method for casting to a float"""
        return self._get(var, default=default, cast=float, force=force)

    def int(self, var, default=NOTSET, force=True):
        """Convenience method for casting to an int"""
        return self._get(var, default=default, cast=int, force=force)

    def str(self, var, default=NOTSET, force=True):
        """Convenience method for casting to a str"""
        return self._get(var, default=default, cast=text_type, force=force)

    # Builtin collections

    def tuple(self, var, default=NOTSET, cast=None, force=True):
        """Convenience method for casting to a tuple

        Note:
            Casting
        """
        return self._get(var, default=default, cast=(cast,), force=force)

    def list(self, var, default=NOTSET, cast=None, force=True):
        """Convenience method for casting to a list

        Note:
            Casting
        """
        return self._get(var, default=default, cast=[cast], force=force)

    def set(self, var, default=NOTSET, cast=None, force=True):
        """Convenience method for casting to a set

        Note:
            Casting
        """
        return self._get(var, default=default, cast={cast}, force=force)

    def dict(self, var, default=NOTSET, cast=None, force=True):
        """Convenience method for casting to a dict

        Note:
            Casting
        """
        return self._get(var, default=default, cast={str: cast}, force=force)

    # Other types

    def decimal(self, var, default=NOTSET, force=True):
        """Convenience method for casting to a decimal.Decimal

        Note:
            Casting
        """
        return self._get(var, default=default, cast=Decimal, force=force)

    def json(self, var, default=NOTSET, force=True):
        """Get environment variable, parsed as a json string"""
        return self._get(var, default=default, cast=json.loads, force=force)

    def url(self, var, default=NOTSET, force=True):
        """Get environment variable, parsed with urlparse/urllib.parse"""
        return self._get(var, default=default, cast=urlparse.urlparse,
                         force=force)

    # Private API

    def _get(self, var, default=NOTSET, cast=None, force=True):
        # Find the value in the environ
        # If the value is missing, use the default or raise an error
        try:
            value = self.environ[var]
        except KeyError:
            if default is NOTSET:
                msg = "Set the environment variable '{}'".format(var)
                raise ImproperlyConfigured(msg)
            else:
                value = default

        # Cast value if:
        #  1. it is different than the default
        #  2. we force, and default different from None
        if (value != default) or (force and default is not None):
            value = self._cast(var, value, cast)

        return value

    def _cast(self, var, value, cast):
        if cast is None:
            pass

        elif cast is bool:
            if not isinstance(value, bool):
                if value is True or value.lower() == 'true':
                    value = True
                elif value is False or value.lower() == 'false':
                    value = False
                else:
                    msg = ("Environment variable '{}' could not be parsed "
                           "as bool: value {} must be 'true' or 'false'")
                    raise ImproperlyConfigured(msg.format(var, value))

        elif cast is int:
            # Allow _ as separators to increase legibility
            if isinstance(value, string_types):
                value = value.replace('_', '')
            try:
                value = int(value)
            except ValueError as e:
                msg = ("Environment variable '{}' could not be parsed "
                       "as int: {}")
                raise ImproperlyConfigured(msg.format(var, str(e)))

        elif cast is float:
            # Allow _ as separators to increase legibility
            if isinstance(value, string_types):
                value = value.replace('_', '')
            try:
                value = float(value)
            except ValueError as e:
                msg = ("Environment variable '{}' could not be parsed "
                       "as float: {}")
                raise ImproperlyConfigured(msg.format(var, str(e)))

        elif cast is Decimal:
            try:
                value = Decimal(value)
            except InvalidOperation:
                msg = ("Environment variable '{}' could not be parsed "
                       "as Decimal: {}")
                raise ImproperlyConfigured(msg.format(var, value))

        elif cast in self._lists:
            if isinstance(value, self._lists):
                value = cast(value)
            elif isinstance(value, string_types):
                parts = value.split(',')
                value = cast([p.strip() for p in parts if p.strip()])
            else:
                msg = "Cannot cast environment variable '{}' from {} to {}"
                formatted = msg.format(var, type(value), type(cast))
                raise ImproperlyConfigured(formatted)

        elif isinstance(cast, self._lists):
            if len(cast) != 1:
                msg = ("Cast for environment variable '{}' is not valid: "
                       "cast must be a {} of length 1")
                raise ImproperlyConfigured(msg.format(var, type(cast)))
            # Convert to a list, since sets do not support indexing
            icast = list(cast)[0]
            if (icast in self._collections or
                    isinstance(icast, self._collections)):
                msg = ("Cast for environment variable '{}' is not valid: "
                       "It is not possible to cast to nested collections")
                raise ImproperlyConfigured(msg.format(var))

            parts = self._cast(var, value, type(cast))
            value = type(cast)([self._cast(var, p, icast) for p in parts])

        elif cast is dict:
            if isinstance(value, dict):
                pass
            elif isinstance(value, string_types):
                parts = [i.strip() for i in value.split(',') if i.strip()]
                items = [p.split('=', 1) for p in parts]
                value = {k.strip(): v.strip() for k, v in items}
            else:
                msg = "Cannot cast environment variable '{}' from {} to {}"
                formatted = msg.format(var, type(value), type(cast))
                raise ImproperlyConfigured(formatted)

        elif isinstance(cast, dict):
            if len(cast) != 1:
                msg = ("Cast for environment variable '{}' is not valid: "
                       "cast must be a dict of length 1")
                raise ImproperlyConfigured(msg.format(var))

            keycast, valcast = list(cast.items())[0]
            if (keycast in self._collections or
                    isinstance(keycast, self._collections) or
                    valcast in self._collections or
                    isinstance(valcast, self._collections)):
                msg = ("Cast for environment variable '{}' is not valid: "
                       "It is not possible to cast to nested collections")
                raise ImproperlyConfigured(msg.format(var))

            parts = self._cast(var, value, dict)
            value = {self._cast(var, k, keycast): self._cast(var, v, valcast)
                     for k, v in parts.items()}

        else:
            try:
                value = cast(value)
            except Exception as e:
                msg = ("Cast for environment variable '{}' could not "
                       "be parsed: {}")
                raise ImproperlyConfigured(msg.format(var, str(e)))

        return value


# Export an initialized environment for convenience

env = Environment(os.environ)
