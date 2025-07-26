"""
Main application window for PyPdfPageManager, a tool for managing and manipulating PDF pages.
"""
# # This Python file uses the following encoding: utf-8

import os
from pathlib import Path
import webbrowser
import logging
logger = logging.getLogger()

from PySide6 import QtCore, QtGui, QtWidgets

from ui.widgets.documentOutputTreeWidget import DocumentOutputTreeWidget
from ui.widgets.documentViewerWidget import DocumentViewerWidget
from engine.pdfEngine import PdfEngine

github_url = "https://github.com/shobhitk/pyPdfPageManager"


class PyPdfPageManager(QtWidgets.QMainWindow):

    """
    The main window class for the PDF Page Manager application.
    It provides a user interface for adding, organizing, merging, splitting,
    and generating PDF documents.
    """
    
    def __init__(self, parent: QtWidgets.QWidget = None):
        """
        Initializes the PyPdfPageManager application window.

        Sets up the main window layout, initializes widgets, loads the PDF engine,
        and establishes connections between UI elements and application logic.

        Args:
            parent (QtWidgets.QWidget, optional): The parent widget of this window.
                                                 Defaults to None.
        """
        super().__init__(parent=parent)
        self.document_list = []
        self.setObjectName("PyPdfPageManager")
        self.setEnabled(True)
        self.resize(882, 882)
        self.setAutoFillBackground(False)
        self.pdf_engine = PdfEngine()
        self.setWindowTitle("PDF Page Manager")

        main_frame = QtWidgets.QFrame()
        self.status_bar = self.statusBar()
        self.menu_bar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menu_bar)

        self.menu_bar.setNativeMenuBar(False)

        self.setCentralWidget(main_frame)
        main_frame.setLayout(QtWidgets.QVBoxLayout())
        main_splitter = QtWidgets.QSplitter()
        main_splitter.setOrientation(QtCore.Qt.Horizontal)
        main_frame.layout().addWidget(main_splitter)
        
        input_output_frame = QtWidgets.QFrame()
        input_output_frame.setLayout(QtWidgets.QHBoxLayout())
        main_frame.layout().setContentsMargins(3,3,3,3)
        main_frame.layout().setSpacing(3)

        # self.input_output_splitter = QtWidgets.QSplitter()
        # self.input_output_splitter.setOrientation(QtCore.Qt.Vertical)
        input_output_frame.layout().setContentsMargins(0,0,0,0)
        input_output_frame.layout().setSpacing(3)

        # self.document_input_list_widget = DocumentInputListWidget(parent_widget=self)
        self.document_output_tree_widget = DocumentOutputTreeWidget(parent_widget=self)
        self.document_output_tree_widget.setStyleSheet("""
QTreeWidget::item{
    height: 20px 0;
}

QSplitter::handle {
    border: 1px solid #333333;
    height: 2px;
    background-color: #303030;
    border-radius: 4px;
}

QSplitter::handle:pressed {
    background: #6187ac;
}
QMenuBar {
    margin-bottom: 1px;
    padding-bottom:1px;
}
            """)
        # self.input_output_splitter.addWidget(self.document_input_list_widget)
        # self.input_output_splitter.addWidget(self.document_output_tree_widget)
        input_output_frame.layout().addWidget(self.document_output_tree_widget)

        button_frame = QtWidgets.QFrame()
        button_frame.setLayout(QtWidgets.QHBoxLayout())
        button_frame.layout().setContentsMargins(3,3,3,3)
        button_frame.layout().setSpacing(3)

        button_frame.layout().addWidget(QtWidgets.QLabel("Output:"))
        self.output_line_edit = QtWidgets.QLineEdit()
        button_frame.layout().addWidget(self.output_line_edit)
        self.browse_button = QtWidgets.QPushButton("Browse")
        button_frame.layout().addWidget(self.browse_button)
        self.generate_button = QtWidgets.QPushButton("Generate")
        button_frame.layout().addWidget(self.generate_button)
        self.close_button = QtWidgets.QPushButton("Close")
        button_frame.layout().addWidget(self.close_button)

        main_frame.layout().setStretchFactor(main_splitter, 1)
        main_frame.layout().setStretchFactor(button_frame, 0)

        doc_view_frame = QtWidgets.QFrame()
        doc_view_frame.setLayout(QtWidgets.QVBoxLayout())
        doc_view_frame.layout().setContentsMargins(0,0,0,0)
        doc_view_frame.layout().setSpacing(3)
        main_frame.layout().addWidget(button_frame)
        main_splitter.addWidget(input_output_frame)
        self.doc_view = DocumentViewerWidget()
        doc_view_frame.layout().addWidget(self.doc_view)
        doc_view_frame.setMinimumWidth(500)
        self.output_line_edit.setText(os.path.expanduser("~/Documents/"))
        main_splitter.addWidget(doc_view_frame)
        self.setup_actions()
        self.setup_context_menus()
        self.setup_menu_bar()
        self.make_connections()


    def setup_actions(self):
        """
        Sets up QAction objects for various menu and context menu operations.
        These actions will be linked to specific functions in `make_connections`.
        """
        self.action_new = QtGui.QAction("New")
        self.action_open = QtGui.QAction("Open")
        self.action_save = QtGui.QAction("Save")
        self.action_add_docs = QtGui.QAction("Add PDFs")
        # self.action_remove_docs = QtGui.QAction("Remove PDFs")
        self.action_merge_docs = QtGui.QAction("Merge PDFs")
        self.action_split_docs = QtGui.QAction("Split PDFs")
        self.action_close = QtGui.QAction("Close")
        self.action_new_document = QtGui.QAction("Create New Document")
        self.action_remove_document = QtGui.QAction("Remove Document")


    def setup_menu_bar(self):
        """
        Configures the application's menu bar with 'File' and 'Output Edit' menus.
        Actions defined in `setup_actions` are added to these menus.
        """
        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.addAction(self.action_add_docs)
        self.file_menu.addAction(self.action_merge_docs)
        self.file_menu.addAction(self.action_split_docs)
        self.file_menu.addAction(self.action_close)
        self.menu_bar.addMenu(self.file_menu)

        self.edit_menu = QtWidgets.QMenu("Output Edit")
        self.menu_bar.addMenu(self.edit_menu)
        self.edit_menu.addAction(self.action_new_document)
        self.edit_menu.addAction(self.action_remove_document)


    def setup_context_menus(self):
        """
        Enables custom context menus for the input list and output tree widgets.
        Defines the context menus (`input_menu` and `output_menu`) and populates
        them with relevant actions.
        """
        self.document_output_tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)        

        self.output_menu = QtWidgets.QMenu()
        self.output_menu.addAction(self.action_add_docs)
        self.output_menu.addAction(self.action_merge_docs)
        self.output_menu.addAction(self.action_split_docs)
        self.output_menu.addAction(self.action_new_document)
        self.output_menu.addAction(self.action_remove_document)


    def show_output_context_menu(self, pos: QtCore.QPoint):
        """
        Displays the context menu for the document output tree widget at the given position.

        Args:
            pos (QtCore.QPoint): The position where the context menu was requested,
                                 relative to the widget.
        """
        self.output_menu.exec(self.document_output_tree_widget.mapToGlobal(pos))

    
    def make_connections(self):
        """
        Connects UI signals to their respective slot functions.
        This includes menu actions, button clicks, and custom signals from
        the `DocumentInputListWidget` and `DocumentOutputTreeWidget`.
        """
        # self.document_input_list_widget.customContextMenuRequested.connect(self.show_input_context_menu)
        self.document_output_tree_widget.customContextMenuRequested.connect(self.show_output_context_menu)

        self.action_add_docs.triggered.connect(self.add_docs)
        # self.action_remove_docs.triggered.connect(self.remove_docs)

        self.action_merge_docs.triggered.connect(self.merge_docs)
        self.action_split_docs.triggered.connect(self.split_docs)
        self.action_close.triggered.connect(self.close)

        self.action_new_document.triggered.connect(self.document_output_tree_widget.add_new_document)
        self.action_remove_document.triggered.connect(self.document_output_tree_widget.remove)

        # self.document_input_list_widget.files_added.connect(self.document_output_tree_widget.add_documents)
        # self.document_input_list_widget.document_selected.connect(self.show_document)
        self.document_output_tree_widget.page_selected.connect(self.show_page)
        self.browse_button.clicked.connect(self.set_output_folder)
        self.generate_button.clicked.connect(self.generate_documents)
        self.close_button.clicked.connect(self.close)

    
    def set_output_folder(self):
        """
        Opens a directory dialog to allow the user to select an output folder.
        The selected path is then displayed in the output line edit.
        """
        result = QtWidgets.QFileDialog.getExistingDirectory(
            self, # Use self as parent for dialog
            'Select Directory',
            os.path.expanduser("~/Documents"),
            options=QtWidgets.QFileDialog.ShowDirsOnly)

        if result:
            self.output_line_edit.setText(result)


    def get_output_folder(self) -> str:
        """
        Retrieves the currently set output folder path from the line edit.

        Returns:
            str: The path to the output folder.
        """
        return self.output_line_edit.text()

    
    def add_docs(self):
        """
        Opens a file dialog to allow the user to select PDF files to add.
        Adds the selected PDF files to the input document list.
        """
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, # Use self as parent for dialog
            "Open files",
            os.path.expanduser("~/Documents"),
            "PDF (*.pdf)"
        )
        if file_names:
            for f_name in file_names:
                self.document_list.append(f_name)
            self.doc_view.update_document_list(self.document_list)
            self.document_output_tree_widget.add_documents(file_names)
            self.status_bar.showMessage("Files Added.")


    def merge_docs(self):
        """
        Generates a merge setup based on all documents currently in the input list.
        Clears the current output tree setup and loads the new merge setup.
        """

        output_folder = self.get_output_folder()
        merge_dict = self.pdf_engine.generate_merged_dict(self.document_list, output_folder)
        self.document_output_tree_widget.clear_setup()
        self.document_output_tree_widget.load_setup(merge_dict)
        self.status_bar.showMessage("Merge setup created.")

    def split_docs(self):
        """
        Generates a split setup for each document currently in the input list.
        Clears the current output tree setup and loads the new split setup.
        """
        # document_list = self.document_input_list_widget.get_document_list()
        if not self.document_list:
            self.status_bar.showMessage("No PDFs to split. Add documents to the input list first.")
            return

        output_folder = self.get_output_folder()
        split_dict = self.pdf_engine.generate_split_dict(self.document_list, output_folder)
        self.document_output_tree_widget.clear_setup()
        self.document_output_tree_widget.load_setup(split_dict)
        self.status_bar.showMessage("Split setup created.")

    
    def open_about(self):
        """
        Opens the project's GitHub URL in the default web browser.
        """
        webbrowser.open(github_url)


    def clear_document_from_view(self):
        """
        Unloads any currently displayed PDF from the document viewer.
        """
        self.doc_view.unload_pdf()

    
    def show_document(self, document_path: str):
        """
        Opens and displays the specified PDF document in the document viewer.

        Args:
            document_path (str): The file path of the PDF document to display.
        """
        self.doc_view.open(document_path)

    
    def show_page(self, page_doc_tuple):
        """
        Opens the specified PDF document and navigates to the given page number
        in the document viewer.

        Args:
            document_path (str): The file path of the PDF document.
            page_number (int): The page number to display (1-indexed).
        """
        self.doc_view.open(page_doc_tuple[0], page_doc_tuple[1])
        

    def show_success_dialog(self, generated_files: list):
        """
        Displays a success message box listing the PDF files that were successfully generated.

        Args:
            generated_files (list): A list of file paths (strings) of the generated PDFs.
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Success!")
        msg.setText("These PDF files were successfully generated:\n" + "\n".join(generated_files))
        msg.adjustSize()
        msg.exec_() # Use exec_() for modal dialogs

    
    def show_error_dialog(self, message: str):
        """
        Displays an error message box with the given message.

        Args:
            message (str): The error message to display.
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error!")
        msg.setText(message)
        msg.adjustSize()
        msg.exec_() # Use exec_() for modal dialogs


    def show_confirm_dialog(self, window_title: str, confirm_text: str) -> bool:
        """
        Displays a confirmation dialog with 'OK' and 'Cancel' buttons.

        Args:
            window_title (str): The title of the confirmation dialog.
            confirm_text (str): The message displayed in the confirmation dialog.

        Returns:
            bool: True if the user clicks 'OK', False otherwise.
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle(window_title)
        msg.setText(confirm_text)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.adjustSize()
        result = msg.exec_()
        return result == QtWidgets.QMessageBox.Ok


    def confirm_output(self, output_dict: dict) -> bool:
        """
        Confirms with the user about overwriting existing output files and prevents
        overwriting input files.

        Args:
            output_dict (dict): A dictionary representing the output setup, including
                                'output_dir' and keys for each output document.

        Returns:
            bool: True if the output operation can proceed, False otherwise.
        """
        output_dir = output_dict.get('output_dir', '')
        if not output_dir:
            self.show_error_dialog("Output directory is not set. Please select an output directory.")
            return False

        files_exist = []

        for doc_key in output_dict.keys():
            if doc_key == 'output_dir': # Skip the output_dir entry
                continue
            
            out_file = Path(output_dir) / f"{doc_key}.pdf"
            
            # Check if output file would overwrite an input file
            if str(out_file) in self.document_list:
                self.show_error_dialog(
                    "Output files cannot be the same as the input files. "
                    "Please choose a different output directory or change the Output file names."
                )
                return False
            
            # Check if output file already exists
            if out_file.exists():
                files_exist.append(str(out_file))
        
        if files_exist:
            window_title = "Overwrite Files?"
            confirm_text = (
                "These files already exist:\n" +
                "\n".join(files_exist) +
                "\nAre you sure you want to continue and overwrite them?"
            )
            return self.show_confirm_dialog(window_title, confirm_text)

        return True

    def generate_documents(self):
        """
        Triggers the PDF generation process based on the current output tree setup.
        Confirms with the user about potential file overwrites before proceeding.
        Displays success or error messages after generation.
        """
        output_dict = self.document_output_tree_widget.get_current_setup()

        if not output_dict:
            self.status_bar.showMessage("No output documents defined to generate.")
            self.show_error_dialog("No output documents defined. Please create new documents or add pages to existing ones in the Output Documents panel.")
            return

        confirm = self.confirm_output(output_dict)
        if not confirm:
            return

        self.status_bar.showMessage("Generating PDFs...")
        try:
            result = self.pdf_engine.generate_docs(output_dict)
            if result:
                self.show_success_dialog(result)
                self.status_bar.showMessage("PDFs generated successfully.")
            else:
                self.show_error_dialog("PDF generation completed with no output files. Check your setup.")
                self.status_bar.showMessage("PDF generation completed.")
        except Exception as e:
            logger.exception("Error during PDF generation.")
            self.show_error_dialog(f"An error occurred during PDF generation: {e}")
            self.status_bar.showMessage("PDF generation failed.")
