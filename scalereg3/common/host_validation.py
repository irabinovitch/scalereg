"""Helpers for tweaking Django's host validation."""

import re

from django.http import request as http_request
from django.utils.regex_helper import _lazy_re_compile


def allow_underscore_hostnames():
    """Adjust Django's host regex to allow underscores (used by preview URLs)."""
    http_request.host_validation_re = _lazy_re_compile(
        r'^([a-z0-9._-]+|\[[a-f0-9]*:[a-f0-9.:]+\])(?::([0-9]+))?$',
        re.IGNORECASE,
    )
