# Newick Tree Validator and Formatter

Simple utility to validate and format Newick trees.

## Usage

Validation without formatting:

```bash
./main.py <tree.nwk>
```

In place formatting:

```bash
./main.py <tree.nwk> --inplace
```

Outputting formatted tree to a separate file:

```bash
./main.py <tree.nwk> --outfile <output.nwk>
```

Outputting list of terminal nodes into a text file:

```bash
./main.py <tree.nwk> --terminals <terminals.txt>
```

## Requirements

- Python
- Typer
- BioPython
