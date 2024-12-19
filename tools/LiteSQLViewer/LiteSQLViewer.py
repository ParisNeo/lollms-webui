import sys

from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QFormLayout,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QListWidget, QMainWindow, QMessageBox,
                             QPushButton, QSplitter, QTableView, QVBoxLayout,
                             QWidget)


class AddRecordDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Record")
        self.setGeometry(100, 100, 300, 200)
        self.layout = QFormLayout(self)
        self.line_edits = {}

        for column in columns:
            if column.lower() != "id":  # Exclude the ID field
                line_edit = QLineEdit(self)
                self.layout.addRow(QLabel(column), line_edit)
                self.line_edits[column] = line_edit

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.accept)
        self.layout.addRow(self.submit_button)

    def get_values(self):
        return {
            column: line_edit.text() for column, line_edit in self.line_edits.items()
        }


class LiteSQLViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteSQL Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                margin: 4px 2px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableView {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QListWidget {
                width: 200px;
                background-color: #ffffff;
                border: 1px solid #ddd;
            }
        """
        )

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.model = None
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()

        # Splitter for left sidebar and main view
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)

        # Left sidebar for tables
        self.table_list = QListWidget()
        self.table_list.itemClicked.connect(self.load_table_from_list)
        self.splitter.addWidget(self.table_list)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Database", self)
        self.open_button.clicked.connect(self.open_database)
        self.commit_button = QPushButton("Commit Changes", self)
        self.commit_button.clicked.connect(self.commit_changes)
        self.add_button = QPushButton("Add Record", self)
        self.add_button.clicked.connect(self.add_record)
        self.edit_button = QPushButton("Edit Record", self)
        self.edit_button.clicked.connect(self.edit_record)
        self.delete_button = QPushButton("Delete Record", self)
        self.delete_button.clicked.connect(self.delete_record)
        self.scroll_button = QPushButton("Scroll to Bottom", self)
        self.scroll_button.clicked.connect(
            self.scroll_to_bottom
        )  # Connect to scroll method
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.commit_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.scroll_button)  # Add scroll button to layout
        main_layout.addLayout(button_layout)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_table)
        main_layout.addWidget(self.search_bar)

        # Table view
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table_view.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        main_layout.addWidget(self.table_view)

        self.splitter.addWidget(main_widget)
        self.splitter.setSizes([150, 650])  # Set default sizes for the splitter

        central_widget.setLayout(layout)

    def open_database(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Database",
            "",
            "SQLite Database Files (*.db *.sqlite);;All Files (*)",
        )
        if file_name:
            self.db.setDatabaseName(file_name)
            if not self.db.open():
                QMessageBox.critical(self, "Error", "Could not open database")
                return
            self.load_tables()

    def load_tables(self):
        self.table_list.clear()
        tables = self.db.tables()
        if not tables:
            QMessageBox.warning(self, "Warning", "No tables found in the database")
            return
        self.table_list.addItems(tables)

    def load_table_from_list(self, item):
        table_name = item.text()
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable(table_name)
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns

        self.table_view.setModel(self.proxy_model)

    def filter_table(self, text):
        self.proxy_model.setFilterFixedString(text)

    def add_record(self):
        if not self.model:
            QMessageBox.warning(self, "Warning", "No table selected")
            return

        # Get the column names, excluding the ID field
        columns = [
            self.model.record().fieldName(i)
            for i in range(self.model.record().count())
            if self.model.record().fieldName(i).lower() != "id"
        ]

        # Create and show the dialog
        dialog = AddRecordDialog(columns, self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.get_values()
            self.insert_record(values)

    def insert_record(self, values):
        if not self.model:
            return

        row = self.model.rowCount()
        self.model.insertRow(row)

        for column, value in values.items():
            self.model.setData(
                self.model.index(row, self.model.fieldIndex(column)), value
            )

    def edit_record(self):
        if not self.model:
            QMessageBox.warning(self, "Warning", "No table selected")
            return
        indexes = self.table_view.selectionModel().selectedRows()
        if len(indexes) != 1:
            QMessageBox.warning(self, "Warning", "Please select a single row to edit")
            return
        source_index = self.proxy_model.mapToSource(indexes[0])
        self.table_view.edit(indexes[0])

    def delete_record(self):
        if not self.model:
            QMessageBox.warning(self, "Warning", "No table selected")
            return
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Warning", "Please select row(s) to delete")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(indexes)} row(s)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            for index in sorted(indexes, reverse=True):
                source_index = self.proxy_model.mapToSource(index)
                self.model.removeRow(source_index.row())
            self.model.select()

    def commit_changes(self):
        if self.model:
            if self.model.submitAll():
                QMessageBox.information(
                    self, "Success", "Changes committed successfully."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to commit changes: " + self.model.lastError().text(),
                )

    def scroll_to_bottom(self):
        if self.model and self.model.rowCount() > 0:
            self.table_view.scrollToBottom()  # Scroll to the bottom of the table view


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiteSQLViewer()
    window.show()
    sys.exit(app.exec_())
