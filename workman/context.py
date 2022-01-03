"""
A flatdict is a mutable mapping that supports deeply-nested separable key access,
for example, the following flatdicts are functionally equivalent:

    flatdict({"author": {"name": "Christian"}})
    flatdict({"author.name": "Christian"})
    flatdict({"author/name": "Christian"}, sep="/")

"""
import re

from typing import Any, MutableMapping
from functools import partial, singledispatch
from itertools import groupby


@singledispatch
def flatten(data, sep: str = "."):
    pass


@flatten.register(int)
@flatten.register(float)
@flatten.register(str)
@flatten.register(bool)
def _flatten_primitive(data, _: str = "."):
    return data


@flatten.register
def _flatten_list(data: list, sep: str = "."):
    return list(map(partial(flatten, sep=sep), data))


@flatten.register
def _flatten_dict(data: dict, sep: str = "."):
    out = {}
    for k, v in data.items():
        v = flatten(v)

        if isinstance(v, dict):
            for subk, subv in v.items():
                out[sep.join([k, subk])] = subv

        else:
            out[k] = v

    return out


@singledispatch
def unflatten(data, sep: str = "."):
    pass


@flatten.register(int)
@flatten.register(float)
@flatten.register(str)
@flatten.register(bool)
def _unflatten_primitive(data, _: str = "."):
    return data


@unflatten.register
def _unflatten_list(data: list, sep: str = "."):
    return list(map(partial(unflatten, sep=sep), data))


@unflatten.register
def _unflatten_dict(data: dict, sep: str = "."):
    items = list(sorted(data.items(), key=lambda t: t[0]))
    out = {k: v for k, v in items if sep not in k}

    nestables = filter(lambda i: sep in i[0], items)
    nestables = ((*k.split(sep, 1), v) for k,v in nestables)
    groups = groupby(nestables, key=lambda k: k[0])

    for g, group in groups:
        out[g] = unflatten({k: v for _, k, v in group})

    return out


def deepget(data: dict, keys: list[str]):
    """
    deepget nested keys from a dictionary. Raises a KeyError on the first
    missing sub-keys
    """

    k = keys.pop(0)
    if keys:
        return deepget(data[k], keys)
    else:
        return data[k]


def deepset(data: dict, keys: list[str], value: Any):
    """
    deepset nested keys to a value in a dictionary, filling in nested dictionaries
    when needed.
    """

    if keys:
        k = keys.pop(0)
        subdata = data[k] if k in data else {}
        data[k] = deepset(subdata, keys, value)
        return data

    else:
        return value




def deepdel(data: dict, keys: list[str]):
    """
    deepdel nested keys from a dictionary. Raises a KeyError missing sub-keys
    """

    k = keys.pop(0)
    if keys:
        deepdel(data[k], keys)
    else:
        del data[k]


class flatdict(dict[str, Any]):
    def __init__(self, *args, **kwargs):
        self.sep = kwargs.pop("sep", ".")
        super().__init__(*args, **kwargs)

    def __getitem__(self, k: str) -> Any:
        keys = k.split(self.sep)
        return deepget(self, keys)

    def __setitem__(self, k: str, v: Any) -> None:
        keys = k.split(self.sep)
        deepset(self, keys, v)

    def __delitem__(self, k: str) -> None:
        keys = k.split(self.sep)
        deepdel(self, keys)


Context = flatdict


if __name__ == "__main__":
    fd = flatdict({"author/name": "Christian"}, sep="/")
    print(fd["author/name"])
    print(fd)
    fd["date/year"] = 2021
    print(fd)
