#!/usr/bin/env python
from __future__ import unicode_literals

from .parser import parse_format_symbol
from . import types

class SymbolTransformation(object):
    def __init__(self, source):
        self.nodes = parse_format_symbol(source)

    def __str__(self):
        return ";".join(["%s" % node for node in self.nodes])

    def transform(self, text):
        for node in self.nodes:
            if isinstance(node, types.VariableTransformationType):
                transformation = node.replace({}, variables = {"s": text})
                if transformation:
                    return transformation

    