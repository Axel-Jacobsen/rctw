#! /bin/bash

# autoformat
black .
rustfmt src/*

# mypy
mypy .
