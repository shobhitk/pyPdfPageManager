"""Summary

Attributes:
    logger (TYPE): Description
"""
# # This Python file uses the following encoding: utf-8
import os
import logging
logger = logging.getLogger()


from PySide6 import QtCore, QtGui, QtWidgets

class DocumentInputListWidget(QtWidgets.QListWidget):

    """Summary
    """
    
    files_added = QtCore.Signal(list)
    document_selected = QtCore.Signal(str)

    def __init__(self, parent_widget, parent=None):
        """Summary
        
        Args:
            parent_widget (TYPE): Description
            parent (None, optional): Description
        """
        super().__init__(parent=parent)
        self.document_list = []
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DropOnly)
        self.setSelectionMode(
            QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.itemClicked.connect(self.emit_document_selected)


    def get_document_list(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self.document_list


    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        """Summary
        
        Args:
            event (QtGui.QDragEnterEvent): Description
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        """Summary
        
        Args:
            event (QtGui.QDragMoveEvent): Description
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)


    def dropEvent(self, event: QtGui.QDropEvent):
        """Summary
        
        Args:
            event (QtGui.QDropEvent): Description
        """
        if event.mimeData().hasUrls():
            event.accept()
            files = [str(url.toLocalFile()) for url in event.mimeData().urls() if not os.path.isdir(str(url.toLocalFile())) and str(url.toLocalFile()).endswith(".pdf")]
            self.add_files(files)

        else:
            super().dropEvent(event)


    def add_files(self, document_list, emit=True):
        """Summary
        
        Args:
            document_list (TYPE): Description
            emit (bool, optional): Description
        """
        for f in document_list:
            self.addItem(f)

        self.document_list.extend(document_list)
        self.document_list = list(set(self.document_list))
        if emit:
            self.files_added.emit(document_list)

    
    def emit_document_selected(self, item):
        """Summary
        
        Args:
            item (TYPE): Description
        """
        self.document_selected.emit(item.text())
