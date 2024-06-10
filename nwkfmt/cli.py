#! /usr/bin/env python
import re
from pathlib import Path
from uuid import uuid4

import typer
from Bio import Phylo
from Bio.Phylo import BaseTree

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def recursive_print(
    clade: Phylo.BaseTree.Clade,
    string: list | None = None,
    indent: int = 0,
    last=True,
) -> str:
    if string is None:
        string = []
    if clade.is_terminal():
        string.append("  " * indent + clade.name + ("," if not last else ""))
        return string
    string.append("  " * indent + "(")

    for pos, subclade in enumerate(clade):
        string = recursive_print(subclade, string, indent + 1, pos == len(clade) - 1)
    string.append(
        "  " * indent
        + ")"
        + (clade.name or f"internal_{str(uuid4())[0:8]}")
        + ("," if not last else "")
    )
    return string


@app.command()
def test(  # noqa: C901, PLR0912
    file: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to the file to be processed",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    outfile: Path = typer.Option(None, help="Output file"),  # noqa: B008
    inplace: bool = typer.Option(False, help="Overwrite input file"),
    terminals=typer.Option(None, help="Output path for list of tip names"),  # noqa: B008
    internals=typer.Option(None, help="Output path for list of internal node names"),  # noqa: B008
):
    file_content = Path(file).read_text(encoding="utf-8")
    regex = r"[^ ()\s,]\s+[^ ()\s,;]"

    match = re.search(regex, file_content)
    if match:
        print("Found whitespace in clade names")
        for pos, match in enumerate(re.finditer(regex, file_content)):
            print()
            print(f"Match {pos + 1}:")
            match_start = match.start()
            file_content_lines = file_content.split("\n")
            char_count = 0
            lines = dict(enumerate(file_content_lines))
            for line_number, line in enumerate(file_content_lines):
                char_count += len(line) + 1
                if char_count > match_start:
                    print(f"Line {line_number + 1}: {line}")
                    print(f"Line {line_number + 2}: {lines[line_number + 1]}")
                    break
        print("\nERROR: Invalid input Newick, clade name(s) contain(s) whitespace")
        raise typer.Exit(1)

    trees: list[BaseTree.Tree] = list(Phylo.parse(file, "newick"))
    for tree in trees:
        clade_names = []
        for clade in tree.find_clades():
            # Check for redundant internal nodes
            if not clade.is_terminal() and len(clade.clades) == 1:
                msg = f"Redundant internal node detected named `{clade.name}` after `{clade_names[-1]}`"
                raise Exception(msg)
            if clade.name is None:
                if clade.is_terminal():
                    msg = f"Terminal clade without name detected after {clade_names[-1]}"
                    raise Exception(msg)
                continue
            if not clade.name.strip():
                msg = f"White space only name detected for clade `{clade.name}` after {clade_names[-1]}"
                raise Exception(msg)
            if clade.name in clade_names:
                msg = f"Duplicate name {clade.name} detected"
                raise Exception(msg)
            clade_names.append(clade.name)

        if inplace:
            outfile = file
        if outfile:
            with open(outfile, "w", encoding="utf-8") as f:
                for line in recursive_print(tree.root):
                    f.write(line + "\n")
                f.write(";")
        if terminals:
            with open(terminals, "w", encoding="utf-8") as f:
                for clade in tree.get_terminals():
                    f.write(clade.name + "\n")
        if internals:
            with open(internals, "w", encoding="utf-8") as f:
                for nonterminal in tree.get_nonterminals():
                    f.write(nonterminal.name + "\n")


def entry_point() -> None:
    app()


if __name__ == "__main__":
    entry_point()
