import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6 import QtCore, QtWidgets, QtPdfWidgets, QtPdf

class DocumentViewerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.pdf_view = QtPdfWidgets.QPdfView()
        self.qt_pdf_document = QtPdf.QPdfDocument(self)
        self.layout().addWidget(self.pdf_view)

    def open(self, path, page_number=None):
        self.pdf_view.setDocument(self.qt_pdf_document)
        if page_number:
            self.pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.SinglePage)
            self.page_selected(page_number)
        else:
            self.pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.MultiPage)

        self.qt_pdf_document.load(path)

    def page_selected(self, page_number):
        nav = self.pdf_view.pageNavigator()
        nav.jump(page_number, QtCore.QPoint(), nav.currentZoom())

    def unload_pdf(self):
        self.pdf_view.setDocument(None)


# if __name__ == "__main__":
#     argument_parser = ArgumentParser(description="PDF Viewer",
#                                      formatter_class=RawTextHelpFormatter)
#     argument_parser.add_argument("file", help="The file to open", nargs='?', type=str)
#     argument_parser.add_argument("page_number", help="The page to open", nargs='?', type=int)
#     options = argument_parser.parse_args()

#     a = QtWidgets.QApplication(sys.argv)
#     w = DocumentViewerWidget()
#     w.show()
#     if options.file:
#         w.open(options.file, options.page_number)

#     # w.unload_pdf()
#     sys.exit(QtCore.QCoreApplication.exec())
