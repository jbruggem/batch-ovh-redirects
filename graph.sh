#!/bin/bash

./redirects.py graph
ccomps -x redirects.dot | dot | gvpack -array3 | neato -Tpng -n2 -o redirects.png
