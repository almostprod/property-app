from functools import partial
from typing import Any, Callable, Dict, Optional

import arrow


def get_value(dict_obj: Dict, key, default=None, coerce: Callable = None) -> Optional[Any]:

    if default is not None and not callable(default):

        def default():
            return default

    if coerce is None:

        def coerce(x):
            return x

    try:
        result = dict_obj[key]
    except KeyError:
        result = None

    if result is not None:
        try:
            return coerce(result)
        except ValueError:
            pass

    return default() if default else None


get_int = partial(get_value, coerce=int)
get_str = partial(get_value, coerce=str)


def get_utc_datetime(dict_obj: dict, key, dt_format, timezone=None, default=None):

    value = get_value(dict_obj, key, default=default)

    if value is None:
        return None

    dt = arrow.get(value, dt_format)

    if dt is None:
        dt = arrow.get(value)

    if timezone:
        dt = dt.to(timezone)

    return dt.to("utc")
