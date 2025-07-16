"""
A QListWidget subclass for displaying and managing a list of document inputs,
supporting drag-and-drop functionality for PDF files.
"""
# # This Python file uses the following encoding: utf-8
import os
import logging
logger = logging.getLogger()

from PySide6 import QtCore, QtGui, QtWidgets

class DocumentInputListWidget(QtWidgets.QListWidget):

    """
    A custom QListWidget designed to accept document file drops (specifically PDFs)
    and manage a list of these documents. It emits signals when files are added
    or a document is selected.
    """
    
    files_added = QtCore.Signal(list)
    document_selected = QtCore.Signal(str)

    def __init__(self, parent_widget: QtWidgets.QWidget, parent: QtWidgets.QWidget = None):
        """
        Initializes the DocumentInputListWidget.

        Args:
            parent_widget (QtWidgets.QWidget): The parent widget of this list widget.
            parent (QtWidgets.QWidget, optional): The QObject parent. Defaults to None.
        """
        super().__init__(parent=parent)
        self.document_list = []
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DropOnly)
        self.setSelectionMode(
            QtWidgets.QListWidget.SelectionMode.ExtendedSelection)
        self.itemClicked.connect(self.emit_document_selected)


    def get_document_list(self) -> list:
        """
        Returns the current list of added document file paths.

        Returns:
            list: A list of strings, where each string is the path to a document.
        """
        return self.document_list


    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        """
        Handles the drag enter event to determine if the dropped data is acceptable.
        Accepts the event if the mime data contains URLs.

        Args:
            event (QtGui.QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        """
        Handles the drag move event.
        Accepts the event if the mime data contains URLs.

        Args:
            event (QtGui.QDragMoveEvent): The drag move event.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)


    def dropEvent(self, event: QtGui.QDropEvent):
        """
        Handles the drop event. Extracts file paths from dropped URLs,
        filters for PDF files, and adds them to the list.

        Args:
            event (QtGui.QDropEvent): The drop event.
        """
        if event.mimeData().hasUrls():
            event.accept()
            files = [
                str(url.toLocalFile()) for url in event.mimeData().urls()
                if not os.path.isdir(str(url.toLocalFile())) and str(url.toLocalFile()).endswith(".pdf")
            ]
            self.add_files(files)

        else:
            super().dropEvent(event)


    def add_files(self, document_list: list, emit: bool = True):
        """
        Adds a list of document file paths to the QListWidget and the internal document list.
        Emits the files_added signal if 'emit' is True.

        Args:
            document_list (list): A list of document file paths (strings) to add.
            emit (bool, optional): If True, the files_added signal will be emitted. Defaults to True.
        """
        for f in document_list:
            self.addItem(f)

        self.document_list.extend(document_list)
        self.document_list = list(set(self.document_list))  # Remove duplicates
        if emit:
            self.files_added.emit(document_list)

    
    def emit_document_selected(self, item: QtWidgets.QListWidgetItem):
        """
        Emits the document_selected signal with the text of the clicked item.

        Args:
            item (QtWidgets.QListWidgetItem): The QListWidgetItem that was clicked.
        """
        self.document_selected.emit(item.text())


