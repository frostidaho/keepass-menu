#!/bin/sh
autopep8 --in-place --max-line-length 90 --aggressive --aggressive "$@"
