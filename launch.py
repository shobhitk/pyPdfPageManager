import sys
from PySide6 import QtWidgets
from ui.main import PyPdfPageManager

def launch():
    app = QtWidgets.QApplication([])
    widget = PyPdfPageManager()
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch()
    
