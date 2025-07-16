import sys
from PySide6 import QtWidgets
from ui.main import PyPdfPageManager

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = PyPdfPageManager()
    widget.show()
    sys.exit(app.exec())
