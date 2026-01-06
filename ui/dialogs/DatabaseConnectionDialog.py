from ui.widgets.AnimatedComboBox import AnimatedComboBox


from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QTextEdit, QVBoxLayout, QWidget, QStyle


import sys
from pathlib import Path
import re

from ui.widgets.AnimatedButton import AnimatedButton
from ui.widgets.AnimatedGroupBox import AnimatedGroupBox
from ui.widgets.AnimatedLineEdit import AnimatedLineEdit


class DatabaseConnectionDialog(QDialog):
    """Dialog class for establishing a database connection and setup query"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import from Database")
        self.setWindowIcon(QIcon("icons/menu_bar/database.png"))
        self.setMinimumWidth(600)
        self.resize(500, 400)

        self.details = {}

        main_layout = QVBoxLayout(self)

        #type selection
        db_type_layout = QHBoxLayout()
        db_type_layout.addWidget(QLabel("Database Type:"))
        self.db_type_combo = AnimatedComboBox()
        self.db_type_combo.addItems(["SQLite", "PostgreSQL", "MySQL"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        db_type_layout.addWidget(self.db_type_combo)
        main_layout.addLayout(db_type_layout)

        #connection details
        self.connection_group = AnimatedGroupBox("Connection Details", parent=self)
        self.connection_layout = QFormLayout()

        self.host_label = QLabel("Host:")
        self.host_input = AnimatedLineEdit("localhost")
        self.connection_layout.addRow(self.host_label, self.host_input)

        self.port_label = QLabel("Port:")
        self.port_input = AnimatedLineEdit()
        self.connection_layout.addRow(self.port_label, self.port_input)

        self.user_label = QLabel("User:")
        self.user_input = AnimatedLineEdit("postgres")
        self.connection_layout.addRow(self.user_label, self.user_input)

        self.password_label = QLabel("Password:")
        self.password_input = AnimatedLineEdit()
        self.password_input.setEchoMode(AnimatedLineEdit.EchoMode.Password)
        self.connection_layout.addRow(self.password_label, self.password_input)

        self.dbname_label = QLabel("Database:")
        self.dbname_input = AnimatedLineEdit("postgres")
        self.connection_layout.addRow(self.dbname_label, self.dbname_input)

        # SQLITE specific
        self.sqlite_layout = QHBoxLayout()
        self.sqlite_label = QLabel("Database File:")
        self.sqlite_path_input = AnimatedLineEdit()
        self.sqlite_path_input.setPlaceholderText("Click 'Browse' to select a .db, .sqlite, or .sqlite3 file")
        self.sqlite_browse_btn = AnimatedButton("Browse", parent=self)
        self.sqlite_browse_btn.clicked.connect(self.browse_sqlite_file)
        self.sqlite_layout.addWidget(self.sqlite_path_input)
        self.sqlite_layout.addWidget(self.sqlite_browse_btn)
        self.sqlite_widget = QWidget()
        self.sqlite_widget.setLayout(self.sqlite_layout)
        self.connection_layout.addRow(self.sqlite_label, self.sqlite_widget)

        self.connection_group.setLayout(self.connection_layout)
        main_layout.addWidget(self.connection_group)

        #querey editor
        query_group = AnimatedGroupBox("SQL Query", parent=self)
        query_layout = QVBoxLayout()
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("Enter your SQL query here, e.g.,\nSELECT * FROM my_table LIMIT 1000;")
        self.query_editor.setFontFamily("JetBrains Mono")
        self.query_editor.setMinimumHeight(150)
        query_layout.addWidget(self.query_editor)

        #query validation
        self.query_status_icon = QLabel()
        self.query_status_icon.setFixedSize(16, 16)
        self.query_status_label = QLabel(" ")
        self.query_status_label.setStyleSheet("font-weight: bold;")

        status_layout = QHBoxLayout()
        status_layout.setSpacing(6)
        status_layout.addWidget(self.query_status_icon)
        status_layout.addWidget(self.query_status_label)
        status_layout.addStretch()
        query_layout.addLayout(status_layout)

        query_group.setLayout(query_layout)
        main_layout.addWidget(query_group)

        #buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.query_editor.textChanged.connect(self.on_query_changed)

        self.on_db_type_changed("SQLite")
        self.on_query_changed()

    def on_query_changed(self) -> None:
        """Validate the query"""
        query = self.query_editor.toPlainText().strip()

        if not query:
            self._set_query_status(
                "Query cannot be empty",
                valid=False
            )
            return
        
        if self._is_valid_select_query(query):
            self._set_query_status(
                "Valid SELECT query",
                valid=True
            )
        else:
            self._set_query_status(
                "Invalid query (Must be a SELECT * FROM statement)",
                valid=False
            )
    
    def _is_valid_select_query(self, query: str) -> bool:
        """Checks if the query entered matches expression rules

        Args:
            query (str): Takes the query from te query text box

        Returns:
            bool: Returns True if the query is valid
        """
        query = re.sub(r"^\s*(--.*\n|/\*.*?\*/\s*)*", "", query, flags=re.S)

        select_pattern = re.compile(
            r"^select\s+.+\s+from\s+.+",
            re.IGNORECASE | re.DOTALL
        )

        return bool(select_pattern.match(query))
    
    def _set_query_status(self, message: str, *, valid: bool) -> None:
        """Sets the status icon and status label based on whether the expression is valid"""
        style = self.style()

        if valid:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
            color = "#388e3c"
        else:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
            color = "#d32f2f"
        
        self.query_status_icon.setPixmap(icon.pixmap(16, 16))
        self.query_status_label.setText(f"{message}")
        self.query_status_label.setStyleSheet(
            f"color: {color}; font-weight: bold;"
        )
        self.query_status_icon.setVisible(True)
        self.query_status_label.setVisible(True)

    def on_db_type_changed(self, db_type) -> None:
        """Show or hide fields based on db type"""
        is_sqlite = (db_type == "SQLite")

        #toggle server fields
        self.host_label.setVisible(not is_sqlite)
        self.host_input.setVisible(not is_sqlite)
        self.port_label.setVisible(not is_sqlite)
        self.port_input.setVisible(not is_sqlite)
        self.user_label.setVisible(not is_sqlite)
        self.user_input.setVisible(not is_sqlite)
        self.password_label.setVisible(not is_sqlite)
        self.password_input.setVisible(not is_sqlite)
        self.dbname_label.setVisible(not is_sqlite)
        self.dbname_input.setVisible(not is_sqlite)

        #toggle SQLITE fields
        self.sqlite_label.setVisible(is_sqlite)
        self.sqlite_widget.setVisible(is_sqlite)

        #set defaults on port and usr
        if db_type == "PostgreSQL":
            self.port_input.setText("5432")
            self.user_input.setText("postgres")
            self.dbname_input.setText("postgres")
        elif db_type == "MySQL":
            self.port_input.setText("3306")
            self.user_input.setText("root")
            self.dbname_input.setText("")

    def browse_sqlite_file(self) -> None:
        """Open a file dialog to find a local SQLite database file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite Database file",
            "",
            "Database Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        if filepath:
            self.sqlite_path_input.setText(filepath)

    def on_accept(self):
        """Validate the input and build connection string before acception"""
        db_type = self.db_type_combo.currentText()
        query = self.query_editor.toPlainText().strip()
        connection_string = ""

        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a SQL query.")
            return

        if not query.lower().startswith("select"):
            QMessageBox.warning(
                self,
                "Invalid Query Syntax",
                "The SQL query must be a 'SELECT' statement."
            )
            return

        try:
            if db_type == "SQLite":
                db_path = self.sqlite_path_input.text().strip()
                if not db_path:
                    QMessageBox.warning(self, "Input Error", "Please provide a path to the SQLite database file.")
                    return
                db_path_abs = str(Path(db_path).resolve())
                if sys.platform == "win32":
                    connection_string = f"sqlite:///{db_path_abs}"
                else:
                    connection_string = f"sqlite:///{db_path_abs}"

            else:
                host = self.host_input.text().strip()
                port = self.port_input.text().strip()
                user = self.user_input.text().strip()
                password = self.password_input.text().strip()
                dbname = self.dbname_input.text().strip()

                if not all([host, port, user, dbname]):
                    QMessageBox.warning(self, "Input Error", "Please fill in all connection details (Host, Port, User, Database).")
                    return

                if db_type == "PostgreSQL":
                    # postgresqsl+psycopg2://user:password@host:port/dbname
                    connection_string = f"Postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
                elif db_type == "MySQL":
                    # mysql+mysqlconnector://user:password@host:port/dbname
                    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"

            self.details = {
                "db_type": db_type,
                "connection_string": connection_string,
                "query": query
            }
            self.accept()

        except Exception as AcceptDatabaseConnectionError:
            QMessageBox.critical(self, "Error", f"Failed to establish a proper connection string: {str(AcceptDatabaseConnectionError)}")

    def get_details(self):
        """Returns the connection string and query"""
        return self.details.get("db_type"), self.details.get("connection_string"), self.details.get("query")