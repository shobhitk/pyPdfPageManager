"""
PDF Document Management System with Drag-and-Drop Interface

PySide6-based GUI for reorganizing PDF pages between documents using drag-and-drop.

Classes:
    PageDropOverlay: Visual overlay for drag-and-drop feedback
    PageSpinBox: Custom spinbox for page numbering  
    PageDocumentBaseItem: Base class for tree widget items
    DocumentItem: Document container
    PageItem: Individual pages within documents
    DocumentOutputTreeWidget: Main tree widget for document management
"""

import os
import sys
from pathlib import Path
from pprint import pprint

import logging
logger = logging.getLogger(__name__)

from PySide6 import QtCore, QtGui, QtWidgets


class PageDropOverlay(QtWidgets.QWidget):
    """
    Visual overlay for drag-and-drop feedback with semi-transparent blue rectangle.
    """
    
    def __init__(self, parent=None):
        """Initialize the drop overlay widget."""
        super().__init__(parent)
        # Make overlay transparent to mouse events
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAcceptDrops(True)
        self.current_item_rect = QtCore.QRect()
        self.display_text = ""

    def set_overlay_rect(self, rect, display_text=''):
        """Set the overlay rectangle and display text, then update the display."""
        self.current_item_rect = rect
        self.display_text = display_text
        self.setVisible(True)
        self.update()

    def paintEvent(self, event):
        """Draw the overlay rectangle and text."""
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.darkGray, 3))
        
        if not self.current_item_rect.isValid():
            return

        # Draw semi-transparent blue rectangle
        painter.setBrush(QtGui.QColor(64, 150, 254, 75))
        painter.drawRect(self.current_item_rect)
        
        # Draw white text centered
        painter.setPen(QtGui.QColor(255, 255, 255, 255))
        self.customFont = QtGui.QFont('Arial', 15)
        painter.setFont(self.customFont)
        painter.drawText(
            self.current_item_rect.x() + (self.current_item_rect.width() / 2), 
            self.current_item_rect.y() + (self.current_item_rect.height() / 4), 
            self.display_text
        )


class PageSpinBox(QtWidgets.QSpinBox):
    """Custom spinbox with inverted step behavior for page numbering."""
    
    def stepEnabled(self):
        """Determine which step directions are enabled."""
        if self.wrapping() or self.isReadOnly():
            return super().stepEnabled()
        
        ret = QtWidgets.QAbstractSpinBox.StepNone
        if self.value() > self.minimum():
            ret |= QtWidgets.QAbstractSpinBox.StepUpEnabled
        if self.value() < self.maximum():
            ret |= QtWidgets.QAbstractSpinBox.StepDownEnabled
        return ret

    def stepBy(self, steps):
        """Perform step operation with inverted direction."""
        return super().stepBy(-steps)


class PageDocumentBaseItem(QtWidgets.QTreeWidgetItem):
    """Base class for tree widget items with sibling navigation."""
    
    def _get_siblings(self):
        """Get all sibling items excluding self."""
        if not self.parent():
            return

        child_count = self.parent().childCount()
        siblings = [self.parent().child(i) for i in range(child_count) if self.parent().child(i) is not self]
        return siblings


class DocumentItem(PageDocumentBaseItem):
    """
    Tree widget item representing a document container.
    
    Document items can contain multiple page items and support drag-and-drop
    operations. They are not draggable themselves but can accept dropped pages.
    
    Attributes:
        document (str): Name or identifier of the document
    """
    
    def __init__(self, document="", *args):
        """
        Initialize a document item.
        
        Args:
            document (str, optional): Document name or identifier. Defaults to "".
            *args: Additional arguments passed to parent constructor
        """
        super().__init__(*args)
        
        # Configure item flags: not draggable, but accepts drops and is editable
        self.setFlags(
            self.flags() & ~QtCore.Qt.ItemFlag.ItemIsDragEnabled | 
            QtCore.Qt.ItemFlag.ItemIsDropEnabled | 
            QtCore.Qt.ItemFlag.ItemIsEditable
        )
        
        self.document = document
        self.setText(0, self.document)

    def get_children(self):
        """
        Get all child items (pages) of this document.
        
        Returns:
            generator: Generator yielding child PageItem objects
        """
        child_count = self.childCount()
        child_gen = (self.child(i) for i in range(child_count))
        return child_gen


    def update_pages(self):
        index = 1
        for child in self.get_children():
            child.set_page_widget()
            child.setSelected(False)


class PageItem(PageDocumentBaseItem):
    """
    Tree widget item representing a page within a document.
    
    Page items contain information about their source document, source page number,
    and current position within the target document. They support drag-and-drop
    operations and include a spinbox widget for page number adjustment.
    
    Attributes:
        source_page_number (str): Original page number from source document
        source_document (str): Name of the source document
        page_number (int): Current page number in the target document
        page_number_spin (PageSpinBox): Spinbox widget for page number adjustment
    """
    
    def __init__(self, source_page_number, page_number=0, source_document="", *args):
        """
        Initialize a page item.
        
        Args:
            source_page_number (str): Original page number from source document
            page_number (int, optional): Current page number in target document. Defaults to 0.
            source_document (str, optional): Name of source document. Defaults to "".
            *args: Additional arguments passed to parent constructor
        """
        super().__init__(*args)
        
        # Configure item flags: draggable, not drop-enabled, not editable, no children
        self.setFlags(
            self.flags() & QtCore.Qt.ItemFlag.ItemIsDragEnabled |
            ~QtCore.Qt.ItemFlag.ItemIsDropEnabled & 
            ~QtCore.Qt.ItemFlag.ItemIsEditable & 
            ~QtCore.Qt.ItemFlag.ItemNeverHasChildren
        )
        
        self.source_page_number = source_page_number
        self.source_document = source_document
        self.page_number = page_number
        self.page_number_spin = None
        
        # Set display text for tree columns
        self.setText(1, str(self.source_page_number))
        self.setText(2, self.source_document)

    def set_page_number(self, page_number):
        """
        Update the page number for this item.
        
        Args:
            page_number (int): New page number
        """
        if not self.page_number_spin:
            return
        self.page_number = page_number

    def __lt__(self, other):
        """
        Compare this page item with another for sorting purposes.
        
        Args:
            other (PageItem): Another page item to compare with
            
        Returns:
            bool: True if this item should be sorted before the other
        """
        # Use default comparison if no page number is set
        if not self.page_number:
            return super().__lt__(other)
        return self.page_number < other.page_number

    def get_page_number(self):
        """
        Get the current page number.
        
        Returns:
            int: Current page number
        """
        return self.page_number

    def get_source_document(self):
        """
        Get the source document name.
        
        Returns:
            str: Source document name
        """
        return self.source_document

    def get_source_page_num(self):
        """
        Get the original source page number.
        
        Returns:
            str: Source page number
        """
        return self.source_page_number

    def set_page_widget(self, block_signals=False):
        """
        Create and configure the spinbox widget for page number adjustment.
        
        Sets up the spinbox with appropriate range and connects it to the
        page reordering functionality.
        """
        self.page_number_spin = PageSpinBox()
        
        # Set range based on number of pages in parent document
        parent_child_count = self.parent().childCount()
        self.page_number_spin.setRange(1, parent_child_count)
        
        # Update range for all sibling spinboxes
        for sibling in self._get_siblings():
            sibling.page_number_spin.setRange(1, parent_child_count)

        # Set current value and connect change handler
        if block_signals:
            self.page_number_spin.blockSignals(True)

        self.page_number_spin.setValue(self.page_number)
        if block_signals:
            self.page_number_spin.blockSignals(False)

        self.page_number_spin.valueChanged.connect(self.set_pages)
        
        # Add widget to tree widget
        self.treeWidget().setItemWidget(self, 0, self.page_number_spin)


    def set_pages(self, value):
        """
        Handle page number change by reordering pages within the document.
        
        This method removes the current item from its position, inserts it at the
        new position, and updates all sibling page numbers accordingly.
        
        Args:
            value (int): New page number (1-based)
        """
        self.page_number = value
        parent_item = self.parent()
        
        # Remove item from current position
        page_item = parent_item.takeChild(parent_item.indexOfChild(self))
        
        # Insert at new position (convert to 0-based index)
        parent_item.insertChild(value - 1, page_item)
        
        # Update page number and widget
        page_item.set_page_number(value)

        page_item.set_page_widget()
        
        # Update all sibling page numbers
        page_item = parent_item.child(value - 1)
        siblings = page_item._get_siblings()
        
        for sibling in siblings:
            # Block signals to prevent recursive updates
            sibling.page_number_spin.blockSignals(True)
            
            # Update page number based on current position
            new_page_num = parent_item.indexOfChild(sibling) + 1
            sibling.set_page_number(new_page_num)
            sibling.page_number_spin.setRange(1, parent_item.childCount())
            sibling.page_number_spin.setValue(new_page_num)
            
            # Clear selection and focus
            sibling.setSelected(False)
            sibling.page_number_spin.clearFocus()
            
            # Re-enable signals
            sibling.page_number_spin.blockSignals(False)

        # Sort children and select the moved item
        parent_item.sortChildren(0, QtCore.Qt.AscendingOrder)
        page_item.setSelected(True)
        # self.parent().setFocus()


class DocumentOutputTreeWidget(QtWidgets.QTreeWidget):
    """
    Main tree widget for document and page management.
    
    This widget provides a hierarchical view of documents and their pages,
    with drag-and-drop functionality for reorganizing pages between documents.
    Includes visual feedback during drag operations and automatic page numbering.
    
    Attributes:
        item_height (int): Height of tree items in pixels
        parent_widget: Reference to parent widget for accessing related functionality
        page_drop_overlay (PageDropOverlay): Visual overlay for drag-and-drop feedback
        undocumented_item (DocumentItem): Special container for orphaned pages
        
    Signals:
        page_selected (str, int): Emitted when a page is selected (document_name, page_number)
    """
    
    page_selected = QtCore.Signal(tuple)

    def __init__(self, parent_widget, parent=None):
        """
        Initialize the document tree widget.
        
        Args:
            parent_widget: Parent widget providing access to related functionality
            parent (QtWidgets.QWidget, optional): Qt parent widget. Defaults to None.
        """
        super().__init__(parent=parent)
        
        self.item_height = 20
        self.parent_widget = parent_widget
        self.page_drop_overlay = PageDropOverlay(self)
        
        # Configure tree widget
        self.setColumnCount(3)
        self.header().resizeSection(0, 150)
        self.header().resizeSection(1, 75)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        # Set item height styling
        self.setStyleSheet(f"""
            QTreeWidget::item{{ 
                height: {self.item_height}px; 
            }}
        """)

        self.up_action = QtGui.QAction("Move_Up", self)
        self.up_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Up))
        self.up_action.triggered.connect(self.move_item_up)
        self.addAction(self.up_action)
        
        self.down_action = QtGui.QAction("Move_Down", self)
        self.down_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.ShiftModifier | QtCore.Qt.Key_Down))
        self.down_action.triggered.connect(self.move_item_down)
        self.addAction(self.down_action)

        # Configure selection and drag-drop behavior
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setHeaderLabels(["New Page Number", "Source Page Number", "Source Document"])
        self.setDropIndicatorShown(False)
        
        # Initialize with undocumented container
        self.add_undocumented()
        
        # Connect signals
        self.itemClicked.connect(self.emit_page_selected)
        
        # Ensure overlay is on top
        self.page_drop_overlay.raise_()


    def resizeEvent(self, event):
        """
        Handle widget resize events by updating the overlay size.
        
        Args:
            event (QtGui.QResizeEvent): Resize event information
        """
        super().resizeEvent(event)
        # Keep overlay size in sync with tree widget
        self.page_drop_overlay.resize(self.size())


    def move_item_up(self, item):
        """
        QAction to move a page up with Shift + Up key sequence
        """
        item = self.selectedItems()[0]
        item.page_number_spin.setValue(item.page_number_spin.value() - 1)


    def move_item_down(self, item):
        """
        QAction to move a page up with Shift + Up key sequence
        """
        item = self.selectedItems()[0]
        item.page_number_spin.setValue(item.page_number_spin.value() + 1)


    def clear_setup(self):
        """
        Clear all items from the tree and reinitialize with undocumented container.
        """
        self.clear()
        self.add_undocumented()


    def add_documents(self, documents):
        """
        Add multiple documents to the tree widget.
        
        Args:
            documents (list): List of document paths or identifiers
        """
        output_folder = self.parent_widget.get_output_folder()
        current_pdf_dict = self.get_current_setup()
        
        # Generate document dictionary using parent widget's PDF engine
        pdf_dict = self.parent_widget.pdf_engine.generate_dict(documents, output_folder)
        current_pdf_dict.update(pdf_dict)
        
        # Reload the tree with updated data
        self.clear_setup()
        self.load_setup(current_pdf_dict)


    def emit_page_selected(self, item):
        """
        Emit page selection signal when a page item is clicked.
        
        Args:
            item (PageItem): The clicked tree item
        """
        # Only emit signal for page items (items with parents)
        if not item.parent():
            return
        self.page_selected.emit((item.source_document, int(item.source_page_number)))


    def _get_total_item_height(self, item, item_height):
        """
        Calculate the total height of a tree item including all its children.
        
        Args:
            item (QtWidgets.QTreeWidgetItem): Tree item to measure
            item_height (int): Height of individual items
            
        Returns:
            int: Total height in pixels
        """
        if not item:
            return 0
            
        total_height = item_height
        
        # Add height of all children recursively
        for i in range(item.childCount()):
            child_height = self._get_total_item_height(item.child(i), item_height)
            total_height += child_height
            
        return total_height


    def _reparent_item(self, item, new_parent):
        """
        Move an item from its current parent to a new parent.
        
        Args:
            item (PageItem): Item to move
            new_parent (DocumentItem): New parent document
        """
        # Remove from old parent
        old_parent = item.parent()
        item = old_parent.takeChild(old_parent.indexOfChild(item))
        
        # Add to new parent
        new_parent.addChild(item)
        # Update page number and widget
        if new_parent.text(0) == "__UNDOCUMENTED__":
            item.setForeground(1, QtGui.QColor("#333333"))
            item.setForeground(2, QtGui.QColor("#333333"))

        else:    
            item.set_page_number(new_parent.childCount())
            item.set_page_widget()


    def dragEnterEvent(self, event: QtGui.QDragMoveEvent) -> None:
        """
        Handle drag enter events to validate drag operations.
        
        Args:
            event (QtGui.QDragMoveEvent): Drag enter event
        """
        # Only allow dragging of page items (items with parents)
        drag_item = self.selectedItems()[0] if self.selectedItems() else None
        if not drag_item or not drag_item.parent():
            event.ignore()
            return
        super().dragEnterEvent(event)


    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        """
        Handle drag move events to show visual feedback and validate drop targets.
        
        Args:
            event (QtGui.QDragMoveEvent): Drag move event
        """
        drag_pos_item = self.itemAt(event.position().toPoint())
        dragged_item = self.currentItem()

        # Validate drop target
        if not drag_pos_item or \
           (dragged_item.parent() is drag_pos_item.parent()) or \
           (drag_pos_item.parent() is None and dragged_item.parent() is drag_pos_item):
            # Invalid drop target - clear overlay
            self.page_drop_overlay.set_overlay_rect(QtCore.QRect())
            event.ignore()
            return

        # Find the top-level document item
        while drag_pos_item.parent():
            drag_pos_item = drag_pos_item.parent()

        # Calculate overlay rectangle
        item_rect = self.visualItemRect(drag_pos_item)
        overlay_height = self._get_total_item_height(drag_pos_item, self.item_height)
        rect = QtCore.QRect(
            item_rect.x(), 
            item_rect.y() + self.header().height(), 
            self.width(), 
            overlay_height
        )
        
        # Show overlay with document name
        self.page_drop_overlay.set_overlay_rect(rect, drag_pos_item.text(0))
        super().dragMoveEvent(event)


    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """
        Handle drop events to move pages between documents.
        
        Args:
            event (QtGui.QDropEvent): Drop event
        """
        # Clear overlay
        self.page_drop_overlay.set_overlay_rect(QtCore.QRect())
        
        # Get drop target
        drop_target_item = self.itemAt(event.position().toPoint())
        if not drop_target_item:
            event.ignore()
            return
            
        # Ensure we're dropping on a document item
        if drop_target_item.parent():
            drop_target_item = drop_target_item.parent()

        dropped_item = self.selectedItems()[0] if self.selectedItems() else None
        if not dropped_item:
            event.ignore()
            return

        # Validate drop operation
        if (drop_target_item.parent() is dropped_item.parent()) or \
           (drop_target_item.parent() is None and dropped_item.parent() is drop_target_item):
            event.ignore()
            return

        # Perform the move operation
        old_parent = dropped_item.parent()
        dropped_item = old_parent.takeChild(old_parent.indexOfChild(dropped_item))
        drop_target_item.addChild(dropped_item)
        
        # Update page number and widget
        if drop_target_item.text(0) != "__UNDOCUMENTED__":
            dropped_item.set_page_number(drop_target_item.childCount())
            dropped_item.set_page_widget()

        else:
            dropped_item.setForeground(1, QtGui.QColor("#333333"))
            dropped_item.setForeground(2, QtGui.QColor("#333333"))


        old_parent.update_pages()

        # Expand all items to show changes
        self.expandAll()
        event.accept()


    def add_undocumented(self):
        """
        Add the special "undocumented" container for orphaned pages.
        """
        self.undocumented_item = DocumentItem(document="__UNDOCUMENTED__")

        self.undocumented_item.setForeground(0, QtGui.QColor("#333333"))

        self.insertTopLevelItem(0, self.undocumented_item)


    def load_setup(self, pdf_dict):
        """
        Load document structure from a dictionary representation.
        
        Args:
            pdf_dict (dict): Dictionary containing document and page information
                Format: {
                    'document_path': {
                        page_number: {source_page_num: source_document}
                    }
                }
        """
        for doc_key in pdf_dict.keys():
            # Skip metadata entries
            if doc_key in ["output_dir"]:
                continue
                
            doc_val = pdf_dict[doc_key]
            doc_base = os.path.basename(doc_key).split(".")[0]
            document_item = DocumentItem(doc_base)
            self.addTopLevelItem(document_item)
            
            # Add pages to document
            for page_key in sorted([int(key) for key in doc_val.keys()]):
                page_val = doc_val[str(page_key)]
                source_page_num = next(iter(page_val))
                page_item = PageItem(
                    source_page_number=source_page_num,
                    page_number=int(page_key),
                    source_document=page_val[source_page_num]
                )
                document_item.addChild(page_item)
                page_item.set_page_widget()
        
        # Expand all items to show structure
        self.expandAll()


    def find_doc_items(self, path):
        """
        Find document items matching a given path.
        
        Args:
            path (str): Path to search for
        """
        root = self.invisibleRootItem()
        # TODO: Implement path-based document search



    def get_current_setup(self):
        """
        Get the current document structure as a dictionary.
        
        Returns:
            dict: Dictionary representation of current document structure
                Format: {
                    'output_dir': str,
                    'document_name': {
                        page_number: {source_page_num: source_document}
                    }
                }
        """
        output_dir = self.parent_widget.output_line_edit.text()
        root = self.invisibleRootItem()
        document_dict = {"output_dir": output_dir}
        
        # Iterate through all document items
        for doc_index in range(root.childCount()):
            document_item = root.child(doc_index)
            
            # Skip the undocumented container
            if document_item.text(0) == "__UNDOCUMENTED__":
                continue
                
            page_count = document_item.childCount()
            if not page_count:
                continue
                
            # Build page dictionary for this document
            page_dict = {}
            for page_index in range(page_count):
                page_item = document_item.child(page_index)
                page_dict[str(page_index + 1)] = {
                    page_item.get_source_page_num(): page_item.get_source_document()
                }
                
            document_dict[document_item.text(0)] = page_dict
        
        return document_dict

    def get_items(self):
        """
        Get all top-level document items.
        
        Returns:
            generator: Generator yielding top-level document items
        """
        root = self.invisibleRootItem()
        child_count = root.childCount()
        child_gen = (root.child(i) for i in range(child_count))
        return child_gen

    def add_new_document(self):
        """
        Add a new document container with user-specified name.
        
        Shows an input dialog for the document name and optionally moves
        selected pages to the new document.
        """
        name, ok = QtWidgets.QInputDialog().getText(
            self,
            "Please Specify the document name.",
            "Document name:"
        )
        if not ok:
            return

        # Get selected page items
        selected_items = None
        if self.selectedItems():
            selected_items = [
                item for item in self.selectedItems() 
                if hasattr(item, 'get_source_document')
            ]

        # Create new document
        doc_item = DocumentItem(name)
        self.addTopLevelItem(doc_item)
        
        # Move selected pages to new document
        if selected_items:
            for item in selected_items:
                self._reparent_item(item, doc_item)

    def remove(self, items=None, source_deleted=False, bypass_confirm=False):
        """
        Remove items from the tree widget.
        
        For document items, moves all child pages to the undocumented container.
        For page items, either moves them to undocumented or deletes them entirely.
        
        Args:
            items (list, optional): Items to remove. If None, uses selected items.
            source_deleted (bool, optional): If True, completely removes page items
                instead of moving to undocumented. Defaults to False.
            bypass_confirm (bool, optional): If True, skips confirmation dialog.
                Defaults to False.
        """
        if not items:
            items = self.selectedItems()

        if not bypass_confirm:
            result = QtWidgets.QMessageBox.question(
                self,    
                "Delete Items",
                "This will delete the document and move all its pages to UNDOCUMENTED.\n"
                "Are you sure you want to continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if result != QtWidgets.QMessageBox.Yes:
                return
        
        for item in items:
            # Cannot delete the undocumented container
            if item.text(0) == "__UNDOCUMENTED__":
                logger.info("Cannot Delete __UNDOCUMENTED__!")
                continue

            if item.parent():
                self._reparent_item(item, self.undocumented_item)

            else:
                # This is a document item
                # Move all child pages to undocumented container
                child_items = list(item.get_children())
                for child_item in child_items:
                    self._reparent_item(child_item, self.undocumented_item)

                # Remove the document item
                self.invisibleRootItem().removeChild(item)
