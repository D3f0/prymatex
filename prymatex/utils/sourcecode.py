#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import re
import string
import difflib
import unicodedata

# ----------------- EOL tools --------------------
EOLS = (("\r\n", 'nt', 'DOS/Windows (\\r\\n)'), ("\n", 'posix', 'UNIX (\\n)'), ("\r", 'mac', 'Macintosh (\\r)'))

def get_eol_chars(text):
    """Get text EOL characters"""
    for eol_chars, _os_name, _ in EOLS:
        if text.find(eol_chars) > -1:
            return eol_chars

def get_os_name_from_eol_chars(eol_chars):
    """Return OS name from EOL characters"""
    for chars, os_name, _ in EOLS:
        if eol_chars == chars:
            return os_name

def get_eol_chars_from_os_name(os_name):
    """Return EOL characters from OS name"""
    for eol_chars, name, _ in EOLS:
        if name == os_name:
            return eol_chars

def has_mixed_eol_chars(text):
    """Detect if text has mixed EOL characters"""
    eol_chars = get_eol_chars(text)
    if eol_chars is None:
        return False
    correct_text = eol_chars.join((text + eol_chars).splitlines())
    return repr(correct_text) != repr(text)

# ----------------- Python Source tests --------------------
def is_builtin(text):
    """Test if passed string is the name of a Python builtin object"""
    import builtins
    return text in [str(name) for name in dir(__builtin__)
                    if not name.startswith('_')]

def is_keyword(text):
    """Test if passed string is the name of a Python keyword"""
    import keyword
    return text in keyword.kwlist

# ----------------- Text search -------------------------
def subsearch(pattern, text, pstart = 0, tstart = 0, ignoreCase = False):
    if not pattern or not text: []
    if pstart == 0 and ignoreCase:
        pattern = pattern.lower()
        text = text.lower()
    end = len(pattern)
    begin = text.find(pattern, tstart)
    while begin == -1 and end >= 0:
        end -= 1
        begin = text.find(pattern[:end], tstart)
    if end <= 0:
        return []
    return [(pstart, pstart + end, begin, begin + end)] + \
        subsearch(pattern[end:], text, pstart = end, tstart = begin + end)

# ----------------- Text matching -------------------------
def matching_blocks(text1, text2, ratio = 1.0, ignoreCase = False):
    if ignoreCase:
        matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
    else:
        matcher = difflib.SequenceMatcher(None, text1, text2)
    if matcher.ratio() >= ratio:
        print(text1, text2, list(matcher.get_grouped_opcodes()))
        for matches in matcher.get_grouped_opcodes():
            for match in [m for m in matches if m[0] == 'equal']:
                yield match[1:]
