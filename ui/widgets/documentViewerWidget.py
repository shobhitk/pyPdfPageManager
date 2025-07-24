import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6 import QtCore, QtWidgets, QtPdfWidgets, QtPdf

class DocumentViewerWidget(QtWidgets.QWidget):
    """
    A custom QWidget that integrates QtPdfWidgets.QPdfView to display PDF documents.
    It provides functionality to open PDF files and jump to specific pages.
    """
    def __init__(self, parent=None):
        """
        Initializes the DocumentViewerWidget.

        Args:
            parent (QtWidgets.QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0) # Remove margins around the layout
        self.doc_list_combobox = QtWidgets.QComboBox()
        self.layout().addWidget(self.doc_list_combobox)
        
        # Initialize QPdfView for displaying PDF content
        self.pdf_view = QtPdfWidgets.QPdfView()
        
        # Initialize QPdfDocument to load and manage the PDF file
        self.qt_pdf_document = QtPdf.QPdfDocument(self)
        
        # Add the QPdfView to the widget's layout
        self.layout().addWidget(self.pdf_view)
        self.doc_list_combobox.currentTextChanged.connect(self.open_file)
        self.update_document_list()


    def update_document_list(self, doc_list=[]):
        self.doc_list_combobox.clear()
        doc_list = ["Show Document"] + doc_list
        self.doc_list_combobox.addItems(doc_list)
        self.doc_list_combobox.setCurrentText("Show Document")


    def open_file(self):
        """
        Calls open function with just the file specified in document viewer combo-box
        """
        self.open(self.doc_list_combobox.currentText())


    def open(self, path: str, page_number: int = 0):
        """
        Opens a PDF document from the given path and optionally jumps to a specific page.

        If a page_number is provided, the viewer is set to single page mode and
        navigates to that page. Otherwise, it defaults to multi-page mode.

        Args:
            path (str): The file path to the PDF document.
            page_number (int, optional): The 0-indexed page number to display.
                                         If None, the document opens in multi-page mode.
                                         Defaults to None.
        """
        if path == "Show Document":
            self.unload_pdf()
            return

        # Associate the QPdfView with the QPdfDocument
        self.pdf_view.setDocument(self.qt_pdf_document)
        
        if page_number:
            # Set to single page mode and jump to the specified page
            self.pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.SinglePage)
            self.page_selected(page_number)
        else:
            # Set to multi-page mode if no specific page is requested
            self.pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.MultiPage)

        # Load the PDF document from the specified path
        self.qt_pdf_document.load(path)

    def page_selected(self, page_number: int):
        """
        Jumps the PDF viewer to the specified page number.

        This method is typically called internally after a document is loaded
        or when a user selects a specific page.

        Args:
            page_number (int): The 0-indexed page number to jump to.
        """
        nav = self.pdf_view.pageNavigator()
        # Jump to the specified page, keeping the current position and zoom level
        nav.jump(page_number - 1, QtCore.QPoint(), nav.currentZoom())

    def unload_pdf(self):
        """
        Unloads the currently displayed PDF document from the viewer.
        """
        self.pdf_view.setDocument(None)

