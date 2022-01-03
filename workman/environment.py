import enum

import jinja2


def gocomment(string: str, linelength: int = 80) -> str:
    linelength = linelength - 3
    slices = (
        slice(start, start + linelength - 1)
        for start in range(0, len(string), linelength)
    )
    return "\n".join([f"// {string[s]}" for s in slices])


DefaultEnvironment = jinja2.Environment(
    lstrip_blocks=True,
    trim_blocks=True,
    keep_trailing_newline=True,
)
DefaultEnvironment.globals.update(gocomment=gocomment)


LaTeXEnvironment = jinja2.Environment(
    lstrip_blocks=True,
    trim_blocks=True,
    keep_trailing_newline=True,
    block_start_string="(*",
    block_end_string="*)",
    variable_start_string="((",
    variable_end_string="))",
)


class Environment(enum.Enum):
    default = DefaultEnvironment
    go = DefaultEnvironment
    latex = LaTeXEnvironment
    python = DefaultEnvironment


def get(language: str):
    return getattr(Environment, language).value
