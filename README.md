# Teaching Tools

[![Actions Status](https://github.com/hofbi/teaching-tools/workflows/CI/badge.svg)](https://github.com/hofbi/teaching-tools)
[![Actions Status](https://github.com/hofbi/teaching-tools/workflows/CodeQL/badge.svg)](https://github.com/hofbi/teaching-tools)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/hofbi/teaching-tools/master.svg)](https://results.pre-commit.ci/latest/github/hofbi/teaching-tools/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Teaching tools created for the [Software Engineering Lab](https://www.ei.tum.de/en/lmt/teaching/software-engineering-laboratory/).

Find all documents [online](https://hofbi.github.io/teaching-tools/)

## Paper

If you use our tools or templates please cite our [paper](https://www.researchgate.net/publication/359502253_Teaching_Software_Engineering_As_Programming_Over_Time).

```tex
@inproceedings{hofbauer_2022,
    author    = {Hofbauer, Markus and  Bachhuber, Christoph and  Kuhn, Christopher and  Steinbach, Eckehard},
    title     = {Teaching Software Engineering As Programming Over Time},
    booktitle = {IEEE/ACM 4th International Workshop on Software Engineering Education for the Next Generation},
    address   = {Pittsburgh, PA, USA},
    month     = {May},
    year      = {2022},
    pages     = {1--8},
    isbn      = {978-1-4503-9336-2/22/05},
    publisher = {Association for Computing Machinery},
    url       = {https://doi.org/10.1145/3528231.3528353},
    doi       = {10.1145/3528231.3528353}
}
```

## Documents

Create documents locally. This requires a [docker](https://docs.docker.com/get-docker/) and [docker compose](https://docs.docker.com/compose/install/) installation.

### Slides

```shell
# Generate Slides as pdf
make slides

# Sever slides
make serve
```

### Docs

```shell
# Generate the documentation
make docs
```

## Development

### Dependencies

To be able to build and execute code, either do the development in the docker container [makeappdev/cpp-dev](https://hub.docker.com/r/makeappdev/cpp-dev), which is made easy in Visual Studio Code:

1. Ensure that Docker is installed and running on your machine
1. Open this folder in VS Code
1. Install the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension
1. Open the command palette (`F1` on Windows, `Shift+Ctrl+P` on Linux)
1. Call `Remote-Containers: Reopen in Container`

If you don't want to develop inside a docker container, you can install the dependencies directly on your OS using

```shell
# Install apt packages
./install.sh

# Create a python venv (optional)
uv venv
source .venv/bin/activate

# Install python dependencies
uv pip install -r requirements.txt
```

### Export Files

Run the following command to export the student homework project and all lecture samples using the [File Export](tools/README.md#file-export) module.

```shell
make package
```

### C++

```shell
mkdir -p build      # Create build dir
cd build            # Go to build dir
cmake ..            # CMake
make                # Build
make test           # Run Tests
```

### pre-commit git hooks

#### Setup

We use [pre-commit](https://pre-commit.com/) to manage our git pre-commit hooks.
`pre-commit` is automatically installed from `requirements.txt`.
To set it up, call

```sh
git config --unset-all core.hooksPath # may fail if you don't have any hooks set, but that's ok
pre-commit install --overwrite
```

#### Usage

With `pre-commit`, you don't use your linters/formatters directly anymore, but through `pre-commit`:

```sh
pre-commit run --file path/to/file1.cpp tools/second_file.py  # run on specific file(s)
pre-commit run --all-files  # run on all files tracked by git
pre-commit run --from-ref origin/master --to-ref HEAD  # run on all files changed on current branch, compared to master
pre-commit run <hook_id> --file <path_to_file>  # run specific hook on specific file
```
