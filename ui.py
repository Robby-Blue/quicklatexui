import os
import sys
import latex_writer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtCore import Qt, QMimeData, QUrl

def get_temp_folder():
    if 'TEMP' in os.environ:
        return os.environ['TEMP']
    elif 'TMP' in os.environ:
        return os.environ['TMP']
    else:
        return '/tmp'

folder = get_temp_folder()

class DraggableImage(QLabel):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.text())
        url = QUrl.fromLocalFile(self.file_path)  # Convert file path to QUrl
        mime_data.setUrls([url])  # Set QUrl object
        drag.setMimeData(mime_data)
        
        drag.exec_(Qt.CopyAction)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QuickLaTexUI')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Text Area
        self.text_area = QTextEdit()
        self.text_area.setText(latex_writer.default_latex)
        layout.addWidget(self.text_area)

        # Button
        self.button = QPushButton('Render')
        self.button.clicked.connect(self.button_clicked)
        layout.addWidget(self.button)

        # Image
        self.image_label = DraggableImage(f"{folder}/ltx.png")
        
        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def button_clicked(self):
        text = self.text_area.toPlainText()
        latex_writer.render_latex(text, folder)
        pixmap = QPixmap(f"{folder}/ltx.png")
        self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
