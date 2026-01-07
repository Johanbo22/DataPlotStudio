from ui.widgets.AnimatedComboBox import AnimatedComboBox


from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QTextEdit, QVBoxLayout, QWidget, QStyle, QTreeWidget, QTreeWidgetItem


import sys
from pathlib import Path
import re
from sqlalchemy import create_engine, inspect, text

from ui.widgets.AnimatedButton import AnimatedButton
from ui.widgets.AnimatedGroupBox import AnimatedGroupBox
from ui.widgets.AnimatedLineEdit import AnimatedLineEdit


class DatabaseConnectionDialog(QDialog):
    """Dialog class for establishing a database connection and setup query"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import from Database")
        self.setWindowIcon(QIcon("icons/menu_bar/database.png"))
        self.setMinimumWidth(800)
        self.resize(900, 500)

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
        self.sqlite_layout.setContentsMargins(0, 0, 0, 0)
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

        # Editor Grouping to show both the query and the schema
        editors_layout = QHBoxLayout()
        #querey editor
        query_group = AnimatedGroupBox("SQL Query", parent=self)
        query_layout = QVBoxLayout()
        instructions = (
            "Enter your SQL query below. You can select specific columns and join tables.\n\n"
            "Example:\n"
            "SELECT t1.col_a, t2.col_b FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id;"
        )
        self.info_label = QLabel(instructions)
        self.info_label.setWordWrap(True)
        query_layout.addWidget(self.info_label)
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("SELECT * FROM ...")
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
        editors_layout.addWidget(query_group)

        # Schema viewer
        schema_group = AnimatedGroupBox("Database Schema", parent=self)
        schema_layout = QVBoxLayout()

        self.load_schema_button = AnimatedButton("Load Tables and Columns", parent=self)
        self.load_schema_button.setToolTip("Connect to the database and list all tables and columns")
        self.load_schema_button.clicked.connect(self.fetch_schema)
        schema_layout.addWidget(self.load_schema_button)

        self.schema_tree = QTreeWidget()
        self.schema_tree.setHeaderLabels(["Table / Column", "Type"])
        self.schema_tree.setAlternatingRowColors(True)
        self.schema_tree.setToolTip("Double-click on an item to insert it into the query")
        self.schema_tree.itemDoubleClicked.connect(self.on_schema_double_clicked)
        schema_layout.addWidget(self.schema_tree)

        schema_group.setLayout(schema_layout)
        editors_layout.addWidget(schema_group, stretch=1)

        main_layout.addLayout(editors_layout)

        #buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.query_editor.textChanged.connect(self.on_query_changed)

        self.on_db_type_changed("SQLite")
        self.on_query_changed()

    def fetch_schema(self) -> None:
        """Connects to the DB using the provided details and populates the schema tree with the tables and columns found in the db"""
        try:
            connection_string = self._build_connection_string()

            #Inspect
            engine = create_engine(connection_string)
            inspector = inspect(engine)

            self.schema_tree.clear()
            table_names = inspector.get_table_names()

            for table in table_names:
                table_item = QTreeWidgetItem(self.schema_tree)
                table_item.setText(0, table)
                table_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))

                columns = []
                try:
                    #Use inspector first
                    columns = inspector.get_columns(table)
                except Exception:
                    #Provide a fallback to sqlite
                    if "sqlite" in connection_string.lower():
                        try:
                            with engine.connect() as conn:
                                #Use PRAGMA
                                result = conn.execute(text(f'PRAGMA table_info("{table}")'))
                                columns = [{"name": row[1], "type": row[2]} for row in result]
                        except Exception as FallbackError:
                            print(f"Fallback inspection failed for {table}: {FallbackError}")
                
                if not columns:
                    # If both methods have failed or the table is just empty
                    err_item = QTreeWidgetItem(table_item)
                    err_item.setText(0, "No columns found or an error has occurred during loading")
                    continue

                for col in columns:
                    col_item = QTreeWidgetItem(table_item)
                    #Get names and type
                    col_name = col.get('name', 'Unknown')
                    col_type = col.get('type', 'Unknown')

                    col_item.setText(0, str(col_name))
                    col_item.setText(1, str(col_type))
                    col_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            
            self.schema_tree.expandAll()
        
        except ValueError as DatabaseValueError:
            QMessageBox.warning(self, "Input Error", str(DatabaseValueError))
        except Exception as ConnectionError:
            QMessageBox.critical(self, "Connection Error", f"Failed to fetch schema:\n{str(ConnectionError)}")
            print(F"Connection Error: {str(ConnectionError)}")
    
    def on_schema_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Insert the clicked ite text into the query"""
        text = item.text(0)
        self.query_editor.insertPlainText(text)
        self.query_editor.setFocus()

    def _build_connection_string(self) -> str:
        """Constructs the connection string from inputs"""
        db_type = self.db_type_combo.currentText()

        connection_string = ""

        if db_type == "SQLite":
            db_path = self.sqlite_path_input.text().strip()
            if not db_path:
                raise ValueError("Please provide a path to the SQLite database file.")
            
            db_path_abs = str(Path(db_path).resolve())
            #Handle Windows path for sqlalchemy
            if sys.platform == "win32":
                connection_string = f"sqlite:///{db_path_abs}"
            else:
                connection_string = f"sqlite:///{db_path_abs}"
        
        else:
            host = self.host_input.text().strip()
            port = self.port_input.text().strip()
            user = self.user_input.text().strip()
            password = self.user_input.text().strip()
            dbname = self.dbname_input.text().strip()

            if not all([host, port, user, dbname]):
                raise ValueError("Please fill in all connection details (Host, Port, User, DatabaseName)")
            
            if db_type == "PostgreSQL":
                connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
            elif db_type == "MySQL":
                connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"
        
        return connection_string

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
                "Valid query",
                valid=True
            )
        else:
            self._set_query_status(
                "Invalid query (Must be a SELECT statement with FROM clause)",
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
            path = Path(filepath)
            if path.suffix.lower() not in [".db", ".sqlite", ".sqlite3"]:
                QMessageBox.warning(
                    self,
                    "Invalid File Format",
                    f"The file format {path.suffix.lower()} is not a valid file format\nPlease select a valid SQLite file (.db, .sqlite, .sqlite3)"
                )
                self.browse_sqlite_file()
                return
            
            self.sqlite_path_input.setText(filepath)

    def on_accept(self):
        """Validate the input and build connection string before acception"""
        db_type = self.db_type_combo.currentText()
        query = self.query_editor.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a SQL Query")
            return
        
        if not query.lower().startswith("select"):
            QMessageBox.warning(
                self,
                "Invalid Query Syntax",
                "The SQL query must be a 'SELECT' statement"
            )
            return
        
        try:
            connection_string = self._build_connection_string()

            self.details = {
                "db_type": db_type,
                "connection_string": connection_string,
                "query": query
            }
            self.accept()
        
        except ValueError as InputError:
            QMessageBox.warning(self, "Input Error", str(InputError))
        except Exception as AcceptDatabaseConnectionError:
            QMessageBox.critical(self, "Error", f"Failed to establis a proper connection string: {str(AcceptDatabaseConnectionError)}")

    def get_details(self):
        """Returns the connection string and query"""
        return self.details.get("db_type"), self.details.get("connection_string"), self.details.get("query")