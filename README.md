# Newick Tree Validator and Formatter

Simple utility to validate and format Newick trees.

The main use of this utility is to validate constraint trees used with IQtree2.

IQtree2 can throw hard to understand errors when using constraint trees even if the tree is technically a valid Newick tree.

This utility will catch many of those errors and provide a more detailed error message.

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

## Release

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

To build a release, run:

```bash
poetry build
```

To publish a release to PyPI, run:

```bash
poetry publish
```

To publish the release to Github, run:

```bash
gh release create 0.2.0 dist/*
```
