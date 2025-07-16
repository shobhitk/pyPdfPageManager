"""Summary

Attributes:
    logger (TYPE): Description
"""
# # This Python file uses the following encoding: utf-8
import os
import sys
from pathlib import Path
from pprint import pprint

import logging
logger = logging.getLogger()

from PySide6 import QtCore, QtGui, QtWidgets

class PageDropOverlay(QtWidgets.QWidget):

    """Summary
    """
    
    def __init__(self, parent=None):
        """Summary
        
        Args:
            parent (None, optional): Description
        """
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAcceptDrops(True)
        self.current_item_rect = QtCore.QRect()

    def set_overlay_rect(self, rect, display_text=''):
        """Summary
        
        Args:
            rect (TYPE): Description
            display_text (str, optional): Description
        """
        self.current_item_rect = rect
        self.display_text = display_text
        self.setVisible(True)
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Summary
        
        Args:
            event (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.darkGray, 3))
        if not self.current_item_rect.isValid():
            return

        painter.setBrush(QtGui.QColor(64, 150, 254, 75))
        painter.drawRect(self.current_item_rect)
        painter.setPen(QtGui.QColor(255, 255, 255, 255))
        self.customFont = QtGui.QFont('Arial', 15
)
        painter.setFont(self.customFont)

        painter.drawText(
            self.current_item_rect.x() + (self.current_item_rect.width() / 2), 
            self.current_item_rect.y() + (self.current_item_rect.height() / 4), 
            self.display_text
        )


class PageSpinBox(QtWidgets.QSpinBox):

    """Summary
    """
    
    def stepEnabled(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        if self.wrapping() or self.isReadOnly():
            return super().stepEnabled()
        ret = QtWidgets.QAbstractSpinBox.StepNone
        if self.value() > self.minimum():
            ret |= QtWidgets.QAbstractSpinBox.StepUpEnabled
        if self.value() < self.maximum():
            ret |= QtWidgets.QAbstractSpinBox.StepDownEnabled
        return ret

    def stepBy(self, steps):
        """Summary
        
        Args:
            steps (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        return super().stepBy(-steps)


class PageDocumentBaseItem(QtWidgets.QTreeWidgetItem):

    """Summary
    """
    
    def _get_siblings(self):
        """Method to siblings of a tree-item.
        
        Returns:
            TYPE: List of Tree Items.
        """
        root = self.treeWidget().invisibleRootItem()
        if self.parent():
            root = self.parent()
        child_count = self.parent().childCount()
        siblings = [self.parent().child(i) for i in range(child_count) if self.parent().child(i) is not self]
        return siblings


class DocumentItem(PageDocumentBaseItem):

    """Summary
    
    Attributes:
        document (TYPE): Description
    """
    
    def __init__(self, document="", *args):
        """Summary
        """
        super().__init__(*args)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemFlag.ItemIsDragEnabled | QtCore.Qt.ItemFlag.ItemIsDropEnabled | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.document = document
        self.setText(0, self.document)


    def get_children(self):
        """Method to return generator of items in the tree.
        
        Returns:
            TYPE: Python Generator of items in tree.
        """
        child_count = self.childCount()
        child_gen = (self.child(i) for i in range(child_count))
        return child_gen


class PageItem(PageDocumentBaseItem):

    """Summary
    
    Attributes:
        page_number (TYPE): Description
        page_number_spin (TYPE): Description
        source_document (TYPE): Description
        source_page_number (TYPE): Description
    """
    
    def __init__(self, source_page_number, page_number=0, source_document="", *args):
        """Summary
        
        Args:
            source_page_number (TYPE): Description
            page_number (int, optional): Description
            source_document (str, optional): Description
            *args: Description
        """
        super().__init__(*args)
        self.setFlags(self.flags() & QtCore.Qt.ItemFlag.ItemIsDragEnabled |
                      ~QtCore.Qt.ItemFlag.ItemIsDropEnabled & ~QtCore.Qt.ItemFlag.ItemIsEditable & ~QtCore.Qt.ItemFlag.ItemNeverHasChildren)
        self.source_page_number = source_page_number
        self.source_document = source_document
        self.page_number = page_number
        self.page_number_spin = None
        self.setText(0, self.source_page_number)
        self.setText(2, self.source_document)
 

    def set_page_number(self, page_number):
        """Summary
        
        Args:
            page_number (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        if not self.page_number_spin:
            return

        self.page_number = page_number


    def __lt__(self, other):
        """Summary
        
        Args:
            other (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        # Custom comparison logic
        if not self.page_number:
            super().__lt__(other)
            return

        return self.page_number < other.page_number


    def get_page_number(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self.page_number


    def get_source_document(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self.source_document


    def get_source_page_num(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self.source_page_number


    def set_page_widget(self):
        """Summary
        """
        self.page_number_spin = PageSpinBox()
        self.page_number_spin.setRange(1, self.parent().childCount())
        for sibling in self._get_siblings():
            sibling.page_number_spin.setRange(1, self.parent().childCount())

        self.page_number_spin.setValue(self.page_number)
        self.page_number_spin.valueChanged.connect(self.set_pages)
        self.treeWidget().setItemWidget(self, 1, self.page_number_spin)


    def set_pages(self, value):
        """Summary
        
        Args:
            value (TYPE): Description
        """
        self.page_number = value
        parent_item = self.parent()
        page_item = parent_item.takeChild(self.parent().indexOfChild(self))
        parent_item.insertChild(value-1, page_item)
        page_item.set_page_number(value)
        page_item.set_page_widget()
        page_item = parent_item.child(value-1)
        siblings = page_item._get_siblings()
        for sibling in siblings:
            sibling.page_number_spin.blockSignals(True)
            sibling.set_page_number(parent_item.indexOfChild(sibling) + 1)
            sibling.page_number_spin.setRange(1, parent_item.childCount())
            sibling.page_number_spin.setValue(parent_item.indexOfChild(sibling) + 1)
            sibling.setSelected(False)
            sibling.page_number_spin.clearFocus()
            sibling.page_number_spin.blockSignals(False)

        parent_item.sortChildren(0, QtCore.Qt.AscendingOrder)
        page_item.setSelected(True)


class DocumentOutputTreeWidget(QtWidgets.QTreeWidget):

    """Summary
    
    Attributes:
        item_height (int): Description
        page_drop_overlay (TYPE): Description
        page_selected (TYPE): Description
        parent_widget (TYPE): Description
        undocumented_item (TYPE): Description
    """
    
    page_selected = QtCore.Signal(str, int)

    def __init__(self, parent_widget, parent=None):
        """Summary
        
        Args:
            parent_widget (TYPE): Description
            parent (None, optional): Description
        """
        super().__init__(parent=parent)
        self.item_height = 20
        self.parent_widget = parent_widget
        self.page_drop_overlay = PageDropOverlay(self)
        self.setColumnCount(3)
        self.header().resizeSection(0, 150)
        self.header().resizeSection(1, 75)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.setStyleSheet("""
            QTreeWidget::item{ 
                height: """+ str(self.item_height) + """px 0; 
            }
            """)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setHeaderLabels(["Current Page Number", "Source Page Number", "Source Document"])
        self.setDropIndicatorShown(False)   
        self.add_undocumented()
        self.itemClicked.connect(self.emit_page_selected)
        self.page_drop_overlay.raise_()


    def resizeEvent(self, event):
        """Summary
        
        Args:
            event (TYPE): Description
        """
        super().resizeEvent(event)
        self.page_drop_overlay.resize(self.size()) # Resize overlay to match the tree widget


    def clear_setup(self):
        """Summary
        """
        self.clear()
        self.add_undocumented()

    
    def add_documents(self, documents):
        """Summary
        
        Args:
            documents (TYPE): Description
        """
        output_folder = self.parent_widget.get_output_folder()
        current_pdf_dict = self.get_current_setup()
        pdf_dict = self.parent_widget.pdf_engine.generate_dict(documents, output_folder)
        current_pdf_dict.update(pdf_dict)
        self.clear_setup()
        self.load_setup(current_pdf_dict)


    def emit_page_selected(self, item):
        """Summary
        
        Args:
            item (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        if not item.parent():
            return
        self.page_selected.emit(item.source_document, item.source_page_number)


    def _get_total_item_height(self, item, item_height):
        """Calculates the combined width and height of a QTreeWidgetItem and its children.
        
        Args:
            item (TYPE): Description
            item_height (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        total_height = 0
        if not item:
            return 0

        total_height += item_height

        for i in range(item.childCount()):
            child_height = self._get_total_item_height(item.child(i), item_height)
            total_height += child_height

        return total_height


    def _reparent_item(self, item, new_parent):
        """Summary
        
        Args:
            item (TYPE): Description
            new_parent (TYPE): Description
        """
        item = item.parent().takeChild(item.parent().indexOfChild(item))
        new_parent.addChild(item)
        item.set_page_number(new_parent.childCount())
        item.set_page_widget()


    def dragEnterEvent(self, event: QtGui.QDragMoveEvent) -> None:
        """Summary
        
        Args:
            event (QtGui.QDragMoveEvent): Description
        
        Returns:
            None: Description
        """
        drag_item = self.selectedItems()[0]
        if not drag_item or not drag_item.parent():
            event.ignore()
            return

        super().dragEnterEvent(event)


    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        """Summary
        
        Args:
            event (QtGui.QDragMoveEvent): Description
        
        Returns:
            None: Description
        """
        drag_index = self.indexAt(event.position().toPoint())
        drag_pos_item = self.itemAt(event.position().toPoint())
        dragged_item = self.currentItem()

        if not drag_pos_item or \
            (dragged_item.parent() is drag_pos_item.parent()) or \
            (drag_pos_item.parent() is None and dragged_item.parent() is drag_pos_item):
            self.page_drop_overlay.set_overlay_rect(QtCore.QRect())  # Clear overlay
            event.ignore()
            return

        else:
            while drag_pos_item.parent():
                drag_pos_item = drag_pos_item.parent()


            item_rect = self.visualItemRect(drag_pos_item)
            overlay_height = self._get_total_item_height(drag_pos_item, self.item_height)
            rect = QtCore.QRect(item_rect.x(), item_rect.y() + self.header().height(), self.width(), overlay_height)
            self.page_drop_overlay.set_overlay_rect(rect, drag_pos_item.text(0))
            super().dragMoveEvent(event)


    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """Summary
        
        Args:
            event (QtGui.QDropEvent): Description
        
        Returns:
            None: Description
        """
        self.page_drop_overlay.set_overlay_rect(QtCore.QRect())  # Clear overlay
        drop_index = self.indexAt(event.position().toPoint())
        drop_target_item = self.itemFromIndex(drop_index)
        if drop_target_item.parent():
            drop_target_item = drop_target_item.parent()

        if not drop_target_item:
            event.ignore()
            return

        dropped_item = self.selectedItems()[0]

        if (drop_target_item.parent() is dropped_item.parent()) or \
            (drop_target_item.parent() is None and dropped_item.parent() is drop_target_item):
            event.ignore()
            return

        dropped_item = dropped_item.parent().takeChild(dropped_item.parent().indexOfChild(dropped_item))
        drop_target_item.addChild(dropped_item)
        dropped_item.set_page_number(drop_target_item.childCount())
        dropped_item.set_page_widget()

        self.expandAll()
        event.accept()


    def add_undocumented(self):
        """Summary
        """
        self.undocumented_item = DocumentItem(document="__UNDOCUMENTED__")
        self.insertTopLevelItem(0, self.undocumented_item)


    def load_setup(self, pdf_dict):
        """Summary
        
        Args:
            pdf_dict (TYPE): Description
        """
        for doc_key in pdf_dict.keys():
            if doc_key in ["output_dir"]:
                continue
            
            doc_val = pdf_dict[doc_key]
            doc_base = os.path.basename(doc_key).split(".")[0]
            document_item = DocumentItem(doc_base)
            self.addTopLevelItem(document_item)
            for page_key in sorted(doc_val.keys()):
                page_val = doc_val[page_key]
                source_page_num = next(iter(page_val))
                page_item = PageItem(
                    source_page_number=source_page_num,
                    page_number=int(page_key),
                    source_document=page_val[source_page_num]
                    )
                document_item.addChild(page_item)
                page_item.set_page_widget()
        
        self.expandAll()

    
    def find_doc_items(self, path):
        """Summary
        
        Args:
            path (TYPE): Description
        """
        root = self.invisibleRootItem()
            

    def get_current_setup(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        # return documents dict
        output_dir = self.parent_widget.output_line_edit.text()
        root = self.invisibleRootItem()
        document_dict = {"output_dir": output_dir}
        for doc_index in range(root.childCount()):
            page_dict = {}
            document_item = root.child(doc_index)
            if document_item.text(0) == "__UNDOCUMENTED__":
                continue

            page_count = document_item.childCount()
            if not page_count:
                continue

            for page_index in range(page_count):
                page_item = document_item.child(page_index)
                page_dict[page_index + 1] = {page_item.get_source_page_num(): page_item.get_source_document()}

            document_dict[document_item.text(0)] = page_dict
        
        return document_dict


    def get_items(self):
        """Method to return generator of items under a the tree-item.
        
        Returns:
            TYPE: Python Generator of items in tree.
        """
        root = self.invisibleRootItem()
        child_count = root.childCount()
        child_gen = (root.child(i) for i in range(child_count))
        return child_gen


    def add_new_document(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        name, ok = QtWidgets.QInputDialog().getText(
            self,
            "Please Specify the document name.",
            "Document name:"
        )
        if not ok:
            return

        selected_items = None
        if self.selectedItems():
            selected_items = [item for item in self.selectedItems() if item.get_source_doucment()]

        doc_item = DocumentItem(name)
        self.addTopLevelItem(doc_item)
        if selected_items:
            for item in selected_items:
                self._reparent_item(item, doc_item)


    def remove(self, items=None, source_deleted=False, bypass_confirm=False):
        """Summary
        
        Args:
            items (None, optional): Description
            source_deleted (bool, optional): Description
            bypass_confirm (bool, optional): Description
        
        Returns:
            TYPE: Description
        """
        if not items:
            items = self.selectedItems()

        if not bypass_confirm:
            result = QtWidgets.QMessageBox.question(self,    
                "Delete Items",
                "This will delete the document and move all its pages to UNDOCUMENTED.\n Are you sure you want to continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        else:
            result = True

        if result != QtWidgets.QMessageBox.Yes or result != True:
            return

        for item in items:
            if item.text(0) == "__UNDOCUMENTED__":
                logger.info("Cannot Delete __UNDOCUMENTED__!")
                continue

            if item.parent():
                if not source_deleted:
                    self._reparent_item(item, self.undocumented_item)
                else:
                    self.item.parent().removeChild(item)
            
            else:
                # Reparent pages of doc item to undocumented_item
                child_items = item.get_children()
                if list(child_items):
                    for child_item in child_items:
                        self._reparent_item(child_items, self.undocumented_item)

                # delete doc item pages
                self.invisibleRootItem().removeChild(item)
