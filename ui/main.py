"""Summary
"""
# # This Python file uses the following encoding: utf-8

import os
from pathlib import Path
import webbrowser
import logging
logger = logging.getLogger()

from PySide6 import QtCore, QtGui, QtWidgets

from ui.widgets.documentInputListWidget import DocumentInputListWidget
from ui.widgets.documentOutputTreeWidget import DocumentOutputTreeWidget
from ui.widgets.documentViewerWidget import DocumentViewerWidget
from engine.pdfEngine import PdfEngine

github_url = "https://github.com/shobhitk/pyPdfPageManager"

stylesheet_file = os.path.dirname(__file__) + "/stylesheet.qss"


class PyPdfPageManager(QtWidgets.QMainWindow):

    """Summary
    """
    
    def __init__(self, parent=None):
        """Summary
        """
        super().__init__(parent=parent)
        self.setObjectName("PyPdfPageManager")
        self.setEnabled(True)
        self.resize(882, 882)
        self.setAutoFillBackground(False)
        self.pdf_engine = PdfEngine()
        self.setWindowTitle("PDF Page Manager")

        self.main_frame = QtWidgets.QFrame()
        self.status_bar = self.statusBar()
        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menu_bar)

        self.menu_bar.setNativeMenuBar(False)

        self.setCentralWidget(self.main_frame)
        self.main_frame.setLayout(QtWidgets.QVBoxLayout())
        self.main_splitter = QtWidgets.QSplitter()
        self.main_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.main_frame.layout().addWidget(self.main_splitter)
        
        self.input_output_frame = QtWidgets.QFrame()
        self.input_output_frame.setLayout(QtWidgets.QHBoxLayout())
        self.main_frame.layout().setContentsMargins(3,3,3,3)
        self.main_frame.layout().setSpacing(3)

        self.input_output_splitter = QtWidgets.QSplitter()
        self.input_output_splitter.setOrientation(QtCore.Qt.Vertical)
        self.input_output_frame.layout().addWidget(self.input_output_splitter)
        self.input_output_frame.layout().setContentsMargins(0,0,0,0)
        self.input_output_frame.layout().setSpacing(3)

        self.document_input_list_widget = DocumentInputListWidget(parent_widget=self)
        self.document_output_tree_widget = DocumentOutputTreeWidget(parent_widget=self)
        with open(stylesheet_file, "r") as fh:
            self.document_output_tree_widget.setStyleSheet(fh.read())
        self.input_output_splitter.addWidget(self.document_input_list_widget)
        self.input_output_splitter.addWidget(self.document_output_tree_widget)

        self.button_frame = QtWidgets.QFrame()
        self.button_frame.setLayout(QtWidgets.QHBoxLayout())
        self.button_frame.layout().setContentsMargins(3,3,3,3)
        self.button_frame.layout().setSpacing(3)

        self.button_frame.layout().addWidget(QtWidgets.QLabel("Output:"))
        self.output_line_edit = QtWidgets.QLineEdit()
        self.button_frame.layout().addWidget(self.output_line_edit)
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.button_frame.layout().addWidget(self.browse_button)
        self.generate_button = QtWidgets.QPushButton("Generate")
        self.button_frame.layout().addWidget(self.generate_button)
        self.close_button = QtWidgets.QPushButton("Close")
        self.button_frame.layout().addWidget(self.close_button)

        self.main_frame.layout().setStretchFactor(self.main_splitter, 1)
        self.main_frame.layout().setStretchFactor(self.button_frame, 0)


        self.pdf_view_frame = QtWidgets.QFrame()
        self.pdf_view_frame.setLayout(QtWidgets.QVBoxLayout())
        self.pdf_view_frame.layout().setContentsMargins(0,0,0,0)
        self.pdf_view_frame.layout().setSpacing(3)
        self.main_frame.layout().addWidget(self.button_frame)
        self.main_splitter.addWidget(self.input_output_frame)
        self.pdf_view = DocumentViewerWidget()
        self.pdf_view_frame.layout().addWidget(self.pdf_view)
        self.pdf_view_frame.setMinimumWidth(500)
        self.output_line_edit.setText(os.path.expanduser("~/Documents/"))
        self.main_splitter.addWidget(self.pdf_view_frame)
        self.setup_actions()
        self.setup_context_menus()
        self.setup_menu_bar()
        self.make_connections()


    def setup_actions(self):
        """Summary
        """
        self.action_new = QtGui.QAction("New")
        self.action_open = QtGui.QAction("Open")
        self.action_save = QtGui.QAction("Save")
        self.action_add_pdfs = QtGui.QAction("Add PDFs")
        self.action_remove_pdfs = QtGui.QAction("Remove PDFs")
        self.action_merge_pdfs = QtGui.QAction("Merge PDFs")
        self.action_split_pdfs = QtGui.QAction("Split PDFs")
        self.action_close = QtGui.QAction("Close")
        self.action_new_document = QtGui.QAction("Create New Document")
        self.action_remove_document = QtGui.QAction("Remove Document")


    def setup_menu_bar(self):
        """Summary
        """
        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_add_pdfs)
        self.file_menu.addAction(self.action_remove_pdfs)
        self.file_menu.addAction(self.action_merge_pdfs)
        self.file_menu.addAction(self.action_split_pdfs)
        self.file_menu.addAction(self.action_close)
        self.menu_bar.addMenu(self.file_menu)

        self.edit_menu = QtWidgets.QMenu("Output Edit")
        self.menu_bar.addMenu(self.edit_menu)
        self.edit_menu.addAction(self.action_new_document)
        self.edit_menu.addAction(self.action_remove_document)


    def setup_context_menus(self):
        """Summary
        """
        self.document_input_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.document_output_tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.input_menu = QtWidgets.QMenu()
        self.input_menu.addAction(self.action_add_pdfs)
        self.input_menu.addAction(self.action_remove_pdfs)
        self.input_menu.addAction(self.action_merge_pdfs)
        self.input_menu.addAction(self.action_split_pdfs)

        self.output_menu = QtWidgets.QMenu()
        self.output_menu.addAction(self.action_new_document)
        self.output_menu.addAction(self.action_remove_document)


    def show_input_context_menu(self, pos):
        """Summary
        
        Args:
            pos (TYPE): Description
        """
        self.input_menu.exec(self.document_input_list_widget.mapToGlobal(pos))


    def show_output_context_menu(self, pos):
        """Summary
        
        Args:
            pos (TYPE): Description
        """
        self.output_menu.exec(self.document_output_tree_widget.mapToGlobal(pos))

    
    def make_connections(self):
        """Summary
        """
        self.document_input_list_widget.customContextMenuRequested.connect(self.show_input_context_menu)
        self.document_output_tree_widget.customContextMenuRequested.connect(self.show_output_context_menu)
        self.action_new.triggered.connect(self.create_new_setup)
        self.action_open.triggered.connect(self.open_setup)
        self.action_save.triggered.connect(self.save_setup)

        self.action_add_pdfs.triggered.connect(self.add_pdfs)
        self.action_remove_pdfs.triggered.connect(self.remove_pdfs)

        self.action_merge_pdfs.triggered.connect(self.merge_pdfs)
        self.action_split_pdfs.triggered.connect(self.split_pdfs)
        self.action_close.triggered.connect(self.close)

        self.action_new_document.triggered.connect(self.document_output_tree_widget.add_new_document)
        self.action_remove_document.triggered.connect(self.document_output_tree_widget.remove)

        self.document_input_list_widget.files_added.connect(self.document_output_tree_widget.add_documents)
        self.document_input_list_widget.document_selected.connect(self.show_document)
        self.document_output_tree_widget.page_selected.connect(self.show_page)
        self.browse_button.clicked.connect(self.set_output_folder)
        self.generate_button.clicked.connect(self.generate_documents)
        self.close_button.clicked.connect(self.close)

    
    def set_output_folder(self):
        """Summary
        """
        result = QtWidgets.QFileDialog.getExistingDirectory(
            None, 
            'Select Directory',
            os.path.expanduser("~/Documents"),
            options=QtWidgets.QFileDialog.ShowDirsOnly)

        self.output_line_edit.setText(result)


    def get_output_folder(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self.output_line_edit.text()


    def create_new_setup(self):
        """Summary
        """
        if self.document_output_tree_widget.has_items():
            window_title = "Save File?"
            confirm_text = "Do you want to save the current setup?"
            result = self.show_confirm_dialog(window_title, confirm_text)
            if result:
                self.save_setup()

        self.document_input_list_widget.clear()
        self.document_output_tree_widget.clear()
        self.document_output_tree_widget.add_undocumented()


    def open_setup(self):
        """Summary
        """
        setup_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 
            "Open Setup file", 
            os.path.expanduser("~/Documents"),
            "JSON (*.json)"
        )
        if setup_file:
            pdf_dict = self.pdf_engine.load_setup(setup_file)
            output_dir = pdf_dict['output_dir']
            input_files = self.pdf_engine.extract_input_files(pdf_dict)
            self.output_line_edit.setText(output_dir)
            self.document_input_list_widget.add_files(input_files, emit=False)
            self.document_output_tree_widget.load_setup(pdf_dict)

        self.status_bar.showMessage("Setup Loaded.")
        

    def save_setup(self):
        """Summary
        """
        data = self.document_output_tree_widget.get_current_setup()
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON Files (*.json)")
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self.pdf_engine.save_setup(data, file_name)

        self.status_bar.showMessage("PDF Setup Changed.")

    
    def add_pdfs(self):
        """Summary
        """
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None, 
            "Open files", 
            os.path.expanduser("~/Documents"),
            "PDF (*.pdf)"
        )
        self.document_input_list_widget.add_files(file_names)
        self.status_bar.showMessage("Files Added.")

    def remove_pdfs(self):
        """Summary
        """
        selected_pdfs = self.document_input_list_widget.selectedItems()
        for item in selected_pdfs:
            item_index = self.document_input_list_widget.row(item)
            removed_item = self.document_input_list_widget.takeItem(item_index)

            # clear all pages belonging to that document from the document_output_tree_widget
            item = self.document_output_tree_widget.find_doc_items(removed_item.text())
            if item:
                self.document_output_tree_widget.remove([item], source_deleted=True, bypass_confirm=True)

        self.clear_document_from_view()        
        self.status_bar.showMessage("Files Removed.")


    def merge_pdfs(self):
        """Summary
        """
        document_list = self.document_input_list_widget.get_document_list()
        output_folder = self.get_output_folder()
        merge_dict = self.pdf_engine.generate_merged_dict(document_list, output_folder)
        self.document_output_tree_widget.clear_setup()
        self.document_output_tree_widget.load_setup(merge_dict)

    def split_pdfs(self):
        """Summary
        """
        document_list = self.document_input_list_widget.get_document_list()
        output_folder = self.get_output_folder()
        split_dict = self.pdf_engine.generate_split_dict(document_list, output_folder)
        self.document_output_tree_widget.clear_setup()
        self.document_output_tree_widget.load_setup(split_dict)

    
    def open_about(self):
        """Summary
        """
        webbrowser.open(github_url)


    def clear_document_from_view(self):
        """Summary
        """
        self.pdf_view.unload_pdf()

    
    def show_document(self, document):
        """Summary
        
        Args:
            document (TYPE): Description
        """
        self.pdf_view.open(document)

    
    def show_page(self, document, page_number):
        """Summary
        
        Args:
            document (TYPE): Description
            page_number (TYPE): Description
        """
        self.pdf_view.open(document, page_number)
        


    def show_success_dialog(self, result):
        """Summary
        
        Args:
            result (TYPE): Description
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Success!")
        msg.setText("These PDF files were successfully generated:\n" + "\n".join(result))
        msg.adjustSize()
        msg.show()

    
    def show_error_dialog(self, message):
        """Summary
        
        Args:
            message (TYPE): Description
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error!")
        msg.setText(message)
        msg.adjustSize()
        msg.show()


    def show_confirm_dialog(self, window_title, confirm_text):
        """Summary
        
        Args:
            window_title (TYPE): Description
            confirm_text (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle(window_title)
        msg.setText(confirm_text)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.adjustSize()
        result = msg.exec_()
        return result == QtWidgets.QMessageBox.Ok


    def confirm_output(self, output_dict):
        """Summary
        
        Args:
            output_dict (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        output_dir = output_dict['output_dir']
        files_exist = []
        # check if output file is same as one of the input files. 
        # We cannot allow this as we would be overwriting a file as its being read.
        for doc_key in output_dict.keys():
            out_file = output_dir + "/" + doc_key + ".pdf"
            if os.path.exists(out_file):
                files_exist.append(out_file)
                if out_file in self.document_input_list_widget.get_document_list():
                    self.show_error_dialog("Output files cannot be the same as the input files. Please choose a different output directory or change the Output file names.")
                    return
        
        if files_exist:
            window_title = "Overwrite Files?"
            confirm_text = "These files already exist,\n" + \
                            "\n".join(files_exist) + \
                            "\nAre you sure you want to continue?"
            return self.show_confirm_dialog(window_title, confirm_text)

        return True

    def generate_documents(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        output_dict = self.document_output_tree_widget.get_current_setup()
        confirm = self.confirm_output(output_dict)
        if not confirm:
            return

        result = self.pdf_engine.generate_pdfs(output_dict)
        if result:
            self.show_success_dialog(result)
