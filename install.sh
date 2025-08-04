#!/usr/bin/env bash

set -euxo pipefail

sudo apt-get update
sudo apt-get install -y \
	build-essential \
	clang-format \
	clang-tidy \
	cppcheck \
	iwyu \
	cmake \
	llvm \
	lcov \
	gdb \
	zip

curl -LsSf https://astral.sh/uv/install.sh | sh
