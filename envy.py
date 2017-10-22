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


__version__ = '0.1.0'


NOTSET = type(str('NoValue'), (object,), {})


logger = logging.getLogger(__name__)


class Environment(object):

    _collections = (dict, list, set, tuple)
    _lists = (list, set, tuple)

    def __init__(self, environ=None):
        self.environ = environ if environ else os.environ

    def __call__(self, var, default=NOTSET, cast=None):
        return self._get(var, default=default, cast=cast)

    def __contains__(self, var):
        return var in self.environ

    # Simple builtins

    def bool(self, var, default=NOTSET):
        return self._get(var, default=default, cast=bool)

    def float(self, var, default=NOTSET):
        return self._get(var, default=default, cast=float)

    def int(self, var, default=NOTSET):
        return self._get(var, default=default, cast=int)

    def str(self, var, default=NOTSET):
        return self._get(var, default=default, cast=text_type)

    # Builtin collections

    def tuple(self, var, default=NOTSET, cast=None):
        return self._get(var, default=default, cast=(cast,))

    def list(self, var, default=NOTSET, cast=None):
        return self._get(var, default=default, cast=[cast])

    def set(self, var, default=NOTSET, cast=None):
        return self._get(var, default=default, cast={cast})

    def dict(self, var, default=NOTSET, cast=None):
        return self._get(var, default=default, cast={str: cast})

    # Other types

    def decimal(self, var, default=NOTSET):
        return self._get(var, default=default, cast=Decimal)

    def json(self, var, default=NOTSET):
        return self._get(var, default=default, cast=json.loads)

    def url(self, var, default=NOTSET):
        return self._get(var, default=default, cast=urlparse.urlparse)

    # Private API

    def _get(self, var, default=NOTSET, cast=None):
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

        # We always cast, even if we've got the default value
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
            try:
                value = int(value)
            except ValueError as e:
                msg = ("Environment variable '{}' could not be parsed "
                       "as int: {}")
                raise ImproperlyConfigured(msg.format(var, str(e)))

        elif cast is float:
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

env = Environment()
