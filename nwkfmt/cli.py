#! /usr/bin/env python
from pathlib import Path

import typer

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

@app.command()
def test( 
    file: Path = typer.Argument(
        ...,
        help="Path to the file to be processed",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    outfile: Path = typer.Option(None, help="Output file"),
    inplace: bool = typer.Option(False, help="Overwrite input file"),
    terminals=typer.Option(None, help="Output path for list of tips"),
):
    import re
    from uuid import uuid4

    from Bio import Phylo

    def recursive_print(
        clade: Phylo.BaseTree.Clade,
        string: list = [],
        indent: int = 0,
        last=True,
    ) -> str:
        if clade.is_terminal():
            string.append(
                "  " * indent + clade.name + ("," if not last else "")
            )
            return string
        else:
            string.append("  " * indent + "(")

            for (pos, subclade) in enumerate(clade):
                string = recursive_print(
                    subclade, string, indent + 1, pos == len(clade) - 1
                )
            string.append(
                "  " * indent
                + ")"
                + (
                    clade.name
                    if clade.name
                    else f"internal_{str(uuid4())[0:4]}"
                )
                + ("," if not last else "")
            )
        return string

    with open(file, "r") as f:
        # Check if regex matches
        file_content = f.read()
        regex = "[^ ()\s,]\s+[^ ()\s,;]"

        match = re.search(regex, file_content)
        if match:
            print("Found whitespace in clade names")
            for (pos, match) in enumerate(re.finditer(regex, file_content)):
                print("")
                print(f"Match {pos + 1}:")
                match_start = match.start()
                file_content_lines = file_content.split("\n")
                char_count = 0
                lines = dict(enumerate(file_content_lines))
                for line_number, line in enumerate(file_content_lines):
                    char_count += len(line) + 1
                    if char_count > match_start:
                        print(f"Line {line_number + 1}: {line}")
                        print(f"Line {line_number+2}: {lines[line_number+1]}")
                        break
            print(
                "\nERROR: Invalid input Newick, clade name(s) contain(s) whitespace"
            )
            raise typer.Exit(1)

    trees = list(Phylo.parse(file, "newick"))
    for tree in trees:
        clade_names = []
        for clade in tree.find_clades():
            if clade.name is not None:
                if clade.name in clade_names:
                    raise Exception(f"Duplicate name {clade.name} detected")
                clade_names.append(clade.name)
            elif clade.is_terminal():
                raise Exception(
                    f"Terminal clade without name detected after {clade_names[-1]}"
                )
        if inplace:
            outfile = file
        if outfile:
            with open(outfile, "w") as f:
                for line in recursive_print(tree.root):
                    f.write(line + "\n")
                f.write(";")
        if terminals:
            with open(terminals):
                for clade in tree.get_terminals():
                    f.write(clade.name + "\n")


def entry_point() -> None:
    app()

if __name__ == "__main__":
    entry_point()
