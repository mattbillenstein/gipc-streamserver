#!/usr/bin/env bash

rm -fR .venv

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
