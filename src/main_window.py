import sys
import os
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileSystemModel, QTreeView,
                             QWidget, QSplitter, QMessageBox, QTextEdit, QToolBar, QAction, QStyle, QFileDialog)
from PyQt5.QtGui import QIcon, QImage, QPainter
from PyQt5.QtCore import Qt
from src.parser.parser import parse_lad_fbd_file, parse_tag_table_file
from src.graphical_view import NetworkView
from src.data_model.data_model import PlcBlock, PlcTagTable
from lxml import etree


class MainWindow(QMainWindow):
    def __init__(self, project_path):
        super().__init__()
        self.setWindowTitle("Siemens PLC Code Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # --- Toolbar for actions ---
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        export_action = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Export to PNG", self)
        export_action.triggered.connect(self.export_view_to_image)
        toolbar.addAction(export_action)

        self.project_path = project_path
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(project_path)
        # Don't show all files, just XML for now
        self.fs_model.setNameFilters(["*.xml"])
        self.fs_model.setNameFilterDisables(False)

        self.project_explorer = QTreeView()
        self.project_explorer.setModel(self.fs_model)
        self.project_explorer.setRootIndex(self.fs_model.index(project_path))
        self.project_explorer.setColumnWidth(0, 250)
        self.project_explorer.doubleClicked.connect(self.on_project_explorer_double_clicked)

        self.content_area = QTextEdit("Double-click an XML file in the Project Explorer to view its contents.")
        self.content_area.setReadOnly(True)

        self.properties_view = QTextEdit("Select an item to view its properties.")
        self.properties_view.setReadOnly(True)

        self.main_splitter.addWidget(self.project_explorer)
        self.main_splitter.addWidget(self.content_area)
        self.main_splitter.addWidget(self.properties_view)
        self.main_splitter.setSizes([250, 600, 350])

    def export_view_to_image(self):
        # Check if the current content widget is a NetworkView
        if not isinstance(self.content_area, NetworkView):
            QMessageBox.information(self, "Export Not Available", "There is no graphical view to export.")
            return

        # Open a file dialog to get the save path
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "export.png", "PNG Images (*.png);;All Files (*)")

        if file_path:
            # Get the scene from the NetworkView
            scene = self.content_area.scene()

            # Use the scene's bounding rect to determine the image size
            rect = scene.sceneRect()
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white) # Use white background for better visibility

            painter = QPainter(image)
            scene.render(painter)
            painter.end()

            if image.save(file_path):
                QMessageBox.information(self, "Export Successful", f"Successfully exported view to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to save the image.")

    def on_project_explorer_double_clicked(self, index):
        file_path = self.fs_model.filePath(index)
        if not self.fs_model.isDir(index):
            try:
                plc_obj = None
                if file_path.lower().endswith('.xml'):
                    # Try parsing as a code block first
                    plc_obj = parse_lad_fbd_file(file_path)
                    # If that doesn't return an object, try parsing as a tag table
                    if plc_obj is None:
                        plc_obj = parse_tag_table_file(file_path)

                if plc_obj:
                    self.display_plc_object(plc_obj)
                else:
                    # Handle case where XML is valid but not a recognized block type
                    QMessageBox.information(self, "Info", f"The file '{os.path.basename(file_path)}' is not a recognized PLC block or tag table.")


            except etree.XMLSyntaxError as e:
                print("--- XML PARSE ERROR ---"); traceback.print_exc()
                QMessageBox.critical(self, "XML Parse Error", f"Failed to parse XML file:\\n{file_path}\\n\\nDetails: {e}")
            except Exception as e:
                print(f"--- UNEXPECTED ERROR while processing {file_path} ---"); traceback.print_exc()
                QMessageBox.critical(self, "Error", f"An unexpected error occurred while processing {file_path}:\\n\\n{type(e).__name__}: {e}")

    def display_plc_object(self, plc_obj):
        current_content_widget = self.main_splitter.widget(1)

        if isinstance(plc_obj, PlcBlock):
            # Only replace the widget if it's not already a NetworkView
            if not isinstance(current_content_widget, NetworkView):
                network_view = NetworkView(plc_obj)
                network_view.properties_signal.connect(self.update_properties_view)
                self.main_splitter.replaceWidget(1, network_view)
                self.content_area = network_view
            else:
                # If it is already a NetworkView, just update its content
                self.content_area.plc_block = plc_obj
                self.content_area.draw_block()
            self.update_properties_view("") # Clear properties on new block load

        elif isinstance(plc_obj, PlcTagTable):
            # Only replace if it's not a QTextEdit already
            if not isinstance(current_content_widget, QTextEdit):
                 text_area = QTextEdit(); text_area.setReadOnly(True)
                 self.main_splitter.replaceWidget(1, text_area)
                 self.content_area = text_area

            # Build the tag table string
            tag_text = f"--- Tag Table: {plc_obj.name} ---\\n\\n"
            for tag in plc_obj.tags:
                tag_text += f"Name: {tag.name}\\n"
                tag_text += f"  DataType: {tag.data_type}\\n"
                tag_text += f"  Address: {tag.logical_address or 'N/A'}\\n"
                tag_text += f"  Comment: {tag.comment or ''}\\n---\\n"
            self.content_area.setText(tag_text)
            self.update_properties_view("")
        else:
            if not isinstance(current_content_widget, QTextEdit):
                 text_area = QTextEdit(); text_area.setReadOnly(True)
                 self.main_splitter.replaceWidget(1, text_area)
                 self.content_area = text_area
            self.content_area.setText(f"Unknown object type: {type(plc_obj)}")
            self.update_properties_view("")

    def update_properties_view(self, info_string):
        self.properties_view.setText(info_string)


def main():
    # Set the path to the data directory relative to this script
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    if not os.path.exists(project_root):
        # We need a GUI context to show a message box
        app_check = QApplication.instance()
        if app_check is None: app_check = QApplication(sys.argv)
        QMessageBox.critical(None, "Error", f"The data directory was not found.\\nPlease ensure the 'data' folder exists at the root of the project.\\nLooked for: {project_root}")
        sys.exit(1)

    app = QApplication(sys.argv)
    main_win = MainWindow(project_root)
    main_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
