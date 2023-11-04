#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y \
    build-essential \
    clang-format \
    clang-tidy \
    cppcheck \
    iwyu \
    cmake \
    lcov \
    zip \
    python3-pip
