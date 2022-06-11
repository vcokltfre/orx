from importlib import import_module
from json import loads
from pathlib import Path
from textwrap import indent

from markdown2 import markdown  # type: ignore


def getdoc(modname: str, symbol: str) -> str:
    item = import_module(modname)

    for attr in symbol.split("."):
        item = getattr(item, attr)

    if isinstance(item, type):
        val = item.__init__.__doc__  # type: ignore
    else:
        val = item.__doc__  # type: ignore

    return indent(val, "    ")  # type: ignore


if __name__ == "__main__":
    data = loads(Path("./docs/_doc.json").read_text())
    output = ""

    for module in data["modules"]:
        modname = module["name"]

        funcs: list[str] = []
        clss: list[str] = []

        for funcname in module["functions"]:
            funcdoc = f"\n### Function `{funcname}`\n\n" + getdoc(modname, funcname)
            funcs.append(funcdoc)

        for klass in module["classes"]:
            clsdoc = f"\n### Class `{klass['name']}`\n\n" + getdoc(modname, klass["name"])

            for funcname in klass["functions"]:
                sym = f"{klass['name']}.{funcname}"
                clsdoc += f"\n#### Method `{sym}`\n\n{getdoc(modname, sym)}\n"

            clss.append(clsdoc)

        output += f"\n## Module `{modname}`\n\n"

        for func in funcs:
            output += "\n" + func

        for klass in clss:
            output += "\n" + klass

        output += "\n\n---"

    output = output[:-3]

    header = """
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro&display=swap" rel="stylesheet">
    </head>
    <style>
        body {
            font-family: 'Source Sans Pro', sans-serif;
        }
    </style>
    """

    Path("./docs/index.html").write_text(header + markdown(output))  # type: ignore
