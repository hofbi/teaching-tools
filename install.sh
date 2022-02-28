#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y \
    clang-tidy \
    cppcheck \
    iwyu \
    cmake \
    lcov \
    python3-pip
