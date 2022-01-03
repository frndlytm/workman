import os
import json
import pathlib
from datetime import date

import click
import jinja2
import jinja2.meta

from dotenv import dotenv_values

from workman import context, environment
from workman import pathutil
from workman.pathutil import Here


def get_template(language: str, *template: str):
    directory = Here(__file__).joinpath("workman", "templates", language, *template)
    if not os.path.exists(str(directory)):
        raise NotADirectoryError(str(directory))
    return directory


def prompt_missing_variables(content: str, ctx: context.Context, env: jinja2.Environment):
    # TODO: This isn't finding {{ description }} in doc.go
    variables = jinja2.meta.find_undeclared_variables(env.parse(content))
    for var in variables:
        if var not in ctx:
            val = click.prompt(f"Set `{var}`: ")
            ctx[var] = val

    return bool(variables)


def render(dst: pathlib.Path, ctx: context.Context, env: jinja2.Environment):
    """Render the name and contents of the dst with context"""
    name = env.from_string(dst.name)
    prompt_missing_variables(name, ctx, env)
    dst = dst.replace(dst.parent.joinpath(name.render(ctx)))

    click.echo(f"\t{str(dst)}")
    if dst.is_file():
        with dst.open() as f:
            contents = env.from_string(f.read())
            prompt_missing_variables(contents, ctx, env)
            dst.write_text(contents.render(ctx))

    else:
        for subdst in dst.iterdir():
            render(subdst, ctx, env)


@click.group()
def main():
    pass


@main.command()
@click.argument("language")
@click.argument("template")
@click.argument("path")
def new(language: str, template: str, path: str):
    src, dst = (
        get_template(language, template),
        pathlib.Path(os.getcwd()).joinpath(path),
    )
    ctx, env = (
        context.Context(context.unflatten({
            "name": dst.name,
            "year": date.today().year,
            **dotenv_values(".env"),
        })),
        environment.get(language),
    )

    click.echo(f"new! {str(dst)}")
    click.echo(json.dumps(ctx, indent=2))
    dst.mkdir(parents=True, exist_ok=True)
    pathutil.copytree(src, dst, dirs_exist_ok=True)
    render(dst, ctx, env)


if __name__ == "__main__":
    main()
