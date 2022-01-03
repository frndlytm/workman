import os
import shutil
from pathlib import Path


def Here(path: str = __file__) -> Path:
    return Path(os.path.dirname(os.path.abspath(path)))


def latest(path: Path):
    numbers = [int(s.name) for s in path.iterdir() if s.is_dir() and s.stem.isdigit()]
    return max([0, *numbers]) + 1


def suffixless(path: Path):
    return path.as_posix().replace(path.suffix, "", 1)


def copytree(src: Path, dst: Path, **kwargs):
    """Copy the contents of the cookie-cutter directory"""
    return shutil.copytree(str(src), str(dst), **kwargs)
