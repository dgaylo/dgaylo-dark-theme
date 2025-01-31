#!/usr/bin/env python3
import sys
import json

with open(sys.argv[1], 'r') as f:
    print(json.load(f)["version"])