#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from prymatex.support.syntax import PMXSyntax

class PMXBlockUserData(QtGui.QTextBlockUserData):
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.scopes = []
        #Folding
        self.foldingMark = None
        self.foldedLevel = 0
        self.folded = False
        #Indent
        self.indent = ""
        #Symbols
        self.symbol = None
        #Words
        self.words = []

        self.textHash = None
        
        self.__cache = {}

    def __nonzero__(self):
        return bool(self.scopes)
    
    def getLastScope(self):
        return self.scopes[-1]
    
    def setScopes(self, scopes):
        self.scopes = scopes
        
    def getScopeAtPosition(self, pos):
        #FIXME: Voy a poner algo mentiroso si pos no esta en self.scopes
        scope = self.scopes[pos] if pos < len(self.scopes) else self.scopes[-1]
        return scope
    
    def scopeRange(self, pos):
        ranges = self.scopeRanges()
        range = filter(lambda (scope, start, end): start <= pos <= end, ranges)
        assert len(range) >= 1, "More than one range"
        range = range[0] if len(range) == 1 else None
        return range
    
    def scopeRanges(self, start = 0, end = None):
        #TODO: Cache para scopeRanges, si el hash no cambio retornar lo cacheado sino regenerar
        current = ( self.scopes[start], start ) if start < len(self.scopes) else ("", 0)
        end = end or len(self.scopes)
        scopes = []
        for index, scope in enumerate(self.scopes[start:], start):
            if scope != current[0]:
                scopes.append(( current[0], current[1], index ))
                current = ( scope, index )
        scopes.append(( current[0], current[1], end ))
        return scopes
    
    def isWordInScopes(self, word):
        return word in reduce(lambda scope, scope1: scope + " " + scope1[0], self.scopeRanges(), "")

    def groups(self, name = ""):
        #http://manual.macromates.com/en/language_grammars
        # 11 root groups: comment, constant, entity, invalid, keyword, markup, meta, storage, string, support, variable
        return map(lambda scopeRange: (scopeRange[1], scopeRange[2]), filter(lambda scopeRange: any(map(lambda s: s.startswith(name), scopeRange[0].split())), self.scopeRanges()))

    def wordsByGroup(self, name = ""):
        groups = self.groups(name)
        return filter(lambda word: any(map(lambda group: group[0] <= word[0] and group[1] >= word[1], groups)), self.words)

    #================================================
    # Cache Handle
    #================================================
    def processorState(self):
        return self.__cache["processor_state"]
    
    def setProcessorState(self, processorState):
        self.__cache["processor_state"] = processorState
