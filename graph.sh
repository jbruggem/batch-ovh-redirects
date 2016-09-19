#!/bin/bash

./redirects.py graph
dot redirects.dot -Tpng -o redirects.png
