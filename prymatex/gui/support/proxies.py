from PyQt4 import QtCore, QtGui
from prymatex.mvc.proxies import PMXFlatBaseProxyModel

class PMXBundleTreeProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent = None):
        super(PMXBundleTreeProxyModel, self).__init__(parent)
        self.bundleItemTypeOrder = ["bundle", "command", "dragcommand", "macro", "snippet", "preference", "template", "templatefile", "syntax"]
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        regexp = self.filterRegExp()
        if regexp.isEmpty():
            return True
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        item = index.internalPointer()
        if item.TYPE == "bundle":
            return True
        else:
            return regexp.indexIn(item.TYPE) != -1
        
    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return True
        
    def lessThan(self, left, right):
        leftData = left.internalPointer()
        rightData = right.internalPointer()
        if leftData.TYPE == rightData.TYPE:
            return rightData.name > leftData.name
        else:
            return self.bundleItemTypeOrder.index(rightData.TYPE) > self.bundleItemTypeOrder.index(leftData.TYPE)

class PMXBundleTypeFilterProxyModel(PMXFlatBaseProxyModel):
    def __init__(self, tipos, parent = None):
        super(PMXBundleTypeFilterProxyModel, self).__init__(parent)
        self.tipos = tipos if isinstance(tipos, list) else [ tipos ]
        
    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        item = index.internalPointer()
        return item.TYPE in self.tipos
        
    def comparableValue(self, index):
        node = index.internalPointer()
        return node.name.lower()
    
    def compareIndex(self, xindex, yindex):
        xnode = xindex.internalPointer()
        ynode = yindex.internalPointer()
        return cmp(xnode.name, ynode.name)
    
    def findItemIndex(self, item):
        for num, index in enumerate(self.indexMap()):
            if index.internalPointer() == item:
                return num
    
    def getAllItems(self):
        for index in self.indexMap():
            yield index.internalPointer()

class PMXBundleProxyModel(PMXBundleTypeFilterProxyModel):
    def __init__(self, parent = None):
        super(PMXBundleProxyModel, self).__init__('bundle', parent)
    
    def data(self, index, role):
        if self.sourceModel() is None:
            return QtCore.QVariant()
        
        sIndex = self.mapToSource(index)
        
        if role == QtCore.Qt.CheckStateRole:
            bundle = sIndex.internalPointer()
            return QtCore.Qt.Checked if bundle.disabled else QtCore.Qt.Unchecked
        else:
            return self.sourceModel().data(sIndex, role)

    def columnCount(self, parent):
        return 1
    
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags  
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
    
class PMXSyntaxProxyModel(PMXBundleTypeFilterProxyModel):
    def __init__(self, parent = None):
        super(PMXSyntaxProxyModel, self).__init__('syntax', parent)
    
    def data(self, index, role):
        if self.sourceModel() is None:
            return None
        
        if not index.isValid():
            return None
        
        sIndex = self.mapToSource(index)
        
        if role == QtCore.Qt.DisplayRole and index.column() == 1:
            syntax = sIndex.internalPointer()
            return syntax.trigger
        elif index.column() == 0:
            return self.sourceModel().data(sIndex, role)

    def columnCount(self, parent):
        return 2
    
class PMXThemeStyleTableProxyModel(QtGui.QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        regexp = self.filterRegExp()
        if regexp.isEmpty():
            return True
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        node = index.internalPointer()
        return regexp.exactMatch(unicode(node.item.theme.uuid))
        
    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return True
        
    def lessThan(self, left, right):
        leftData = left.internalPointer()
        rightData = right.internalPointer()
        return rightData.name > leftData.name
