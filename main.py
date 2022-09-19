# Start with Typer CLI boilerplate

import typer
from pathlib import Path

app = typer.Typer()



def main(
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
    outfile: Path = typer.Option(...,help="Output file"),
    inplace: bool = typer.Option(False, help="Overwrite input file"),
):

    from Bio import Phylo
    from uuid import uuid4

    def recursive_print(clade: Phylo.BaseTree.Clade, string: list = [], indent: int = 0, last=True) -> str:
        if clade.is_terminal():
            string.append("  " * indent + clade.name + ("," if not last else ""))
            return string
        else:
            string.append("  " * indent + "(")

            for (pos, subclade) in enumerate(clade):
                string = recursive_print(subclade, string, indent + 1, pos == len(clade) - 1)
            string.append("  " * indent + ")" + (clade.name if clade.name else f"internal_{str(uuid4())[0:4]}") + ("," if not last else ""))
        return string


    trees = list(Phylo.parse(file,"newick"))
    for tree in trees:
        clade_names = []
        for clade in tree.find_clades():
            if clade.name is not None:
                if clade.name in clade_names:
                    raise Exception(f"Duplicate name {clade.name} detected")
                clade_names.append(clade.name)
        if inplace:
            outfile = file
        with open(outfile, "w") as f:
            for line in recursive_print(tree.root):
                f.write(line + "\n")
            f.write(";")

if __name__ == "__main__":
    typer.run(main)
