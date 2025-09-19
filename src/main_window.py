import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                             QTableWidgetItem, QAction, QFileDialog, QDockWidget,
                             QTreeView, QTextEdit, QFileSystemModel, QMessageBox,
                             QStackedWidget)
from PyQt5.QtCore import Qt, QDir
from src.parser import parse_tag_table_file, parse_lad_fbd_file
from src.graphical_view import GraphicalView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Siemens PLC Code Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self._create_project_explorer()
        self._create_properties_pane()

        # Set up the central stacked widget for code viewing
        self.stacked_widget = QStackedWidget()
        self.table_widget = QTableWidget()
        self.graphical_view = GraphicalView()
        self.stacked_widget.addWidget(self.table_widget)
        self.stacked_widget.addWidget(self.graphical_view)
        self.setCentralWidget(self.stacked_widget)

        # Create the menu bar and status bar
        self._create_menu_bar()
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_project_explorer(self):
        self.project_explorer_dock = QDockWidget("Project Explorer", self)
        self.tree_view = QTreeView()
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setRootIndex(self.fs_model.index('data'))
        self.tree_view.doubleClicked.connect(self.on_project_explorer_double_clicked)
        self.project_explorer_dock.setWidget(self.tree_view)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_explorer_dock)

    def _create_properties_pane(self):
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_dock.setWidget(self.properties_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)

    def on_project_explorer_double_clicked(self, index):
        file_path = self.fs_model.filePath(index)
        if self.fs_model.isFile(index):
            self.statusBar().showMessage(f"Opening {file_path}...")
            if "Program_blocks" in file_path:
                self.load_lad_fbd_block(file_path)
            else:
                self.load_tag_table(file_path)

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PLC File",
                                                   "data/", "XML Files (*.xml);;All Files (*)",
                                                   options=options)
        if file_name:
            self.statusBar().showMessage(f"Opening {file_name}...")
            if "Program_blocks" in file_name:
                self.load_lad_fbd_block(file_name)
            else:
                self.load_tag_table(file_name)

    def load_lad_fbd_block(self, file_path):
        plc_block_obj = parse_lad_fbd_file(file_path)
        if plc_block_obj:
            self.stacked_widget.setCurrentWidget(self.graphical_view)
            self.graphical_view.render_block(plc_block_obj)
            self.statusBar().showMessage(f"Successfully loaded {plc_block_obj.name}", 5000)
            self.setWindowTitle(f"Siemens PLC Code Viewer - {plc_block_obj.name}")
        else:
            self.statusBar().showMessage(f"Failed to load or parse file: {file_path}", 5000)
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText(f"Failed to load or parse the file:\n{file_path}")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def load_tag_table(self, file_path):
        tag_table_obj = parse_tag_table_file(file_path)
        if tag_table_obj:
            self.populate_table(tag_table_obj)
            self.statusBar().showMessage(f"Successfully loaded {tag_table_obj.name}", 5000)
        else:
            self.statusBar().showMessage(f"Failed to load or parse file: {file_path}", 5000)
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText(f"Failed to load or parse the file:\n{file_path}")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def populate_table(self, tag_table_obj):
        self.table_widget.setRowCount(len(tag_table_obj.tags))
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Data Type", "Logical Address", "Comment"])

        for row, tag in enumerate(tag_table_obj.tags):
            self.table_widget.setItem(row, 0, QTableWidgetItem(tag.name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(tag.data_type))
            self.table_widget.setItem(row, 2, QTableWidgetItem(tag.logical_address))
            self.table_widget.setItem(row, 3, QTableWidgetItem(tag.comment))

        self.table_widget.resizeColumnsToContents()
        self.setWindowTitle(f"Siemens PLC Code Viewer - {tag_table_obj.name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
