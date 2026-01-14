from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox


from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QTextEdit, QVBoxLayout, QWidget, QStyle, QTreeWidget, QTreeWidgetItem, QSplitter


import sys
from pathlib import Path
import re
from sqlalchemy import create_engine, inspect, text

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class DatabaseConnectionDialog(QDialog):
    """Dialog class for establishing a database connection and setup query"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import from Database")
        self.setWindowIcon(QIcon("icons/menu_bar/database.png"))
        self.setMinimumWidth(900)
        self.resize(100, 600)

        self.details = {}

        main_layout = QVBoxLayout(self)

        #type selection
        db_type_layout = QHBoxLayout()
        db_type_layout.addWidget(QLabel("Database Type:"))
        self.db_type_combo = DataPlotStudioComboBox()
        self.db_type_combo.addItems(["SQLite","DuckDB", "PostgreSQL", "MySQL"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        db_type_layout.addWidget(self.db_type_combo)
        main_layout.addLayout(db_type_layout)

        #connection details
        self.connection_group = DataPlotStudioGroupBox("Connection Details", parent=self)
        self.connection_layout = QFormLayout()

        self.host_label = QLabel("Host:")
        self.host_input = DataPlotStudioLineEdit("localhost")
        self.connection_layout.addRow(self.host_label, self.host_input)

        self.port_label = QLabel("Port:")
        self.port_input = DataPlotStudioLineEdit()
        self.connection_layout.addRow(self.port_label, self.port_input)

        self.user_label = QLabel("User:")
        self.user_input = DataPlotStudioLineEdit("postgres")
        self.connection_layout.addRow(self.user_label, self.user_input)

        self.password_label = QLabel("Password:")
        self.password_input = DataPlotStudioLineEdit()
        self.password_input.setEchoMode(DataPlotStudioLineEdit.EchoMode.Password)
        self.connection_layout.addRow(self.password_label, self.password_input)

        self.dbname_label = QLabel("Database:")
        self.dbname_input = DataPlotStudioLineEdit("postgres")
        self.connection_layout.addRow(self.dbname_label, self.dbname_input)

        # SQLITE and duckDB specific
        self.file_db_layout = QHBoxLayout()
        self.file_db_layout.setContentsMargins(0, 0, 0, 0)
        self.file_db_label = QLabel("Database File:")
        self.file_db_path_input = DataPlotStudioLineEdit()
        self.file_db_path_input.setPlaceholderText("Click 'Browse' to select a database file")
        self.file_db_browse_button = DataPlotStudioButton("Browse", parent=self)
        self.file_db_browse_button.clicked.connect(self.browse_file_db)
        self.file_db_layout.addWidget(self.file_db_path_input)
        self.file_db_layout.addWidget(self.file_db_browse_button)
        self.file_db_widget = QWidget()
        self.file_db_widget.setLayout(self.file_db_layout)
        self.connection_layout.addRow(self.file_db_label, self.file_db_widget)

        # A test connection button
        self.test_connection_wrapper = QWidget()
        test_connection_layout = QHBoxLayout(self.test_connection_wrapper)
        test_connection_layout.setContentsMargins(0, 0, 0, 0)

        # Database icons
        self.db_icon_label = QLabel()
        self.db_icon_label.setFixedHeight(24)
        self.db_icon_label.setStyleSheet("border: none; background: transparent;")
        test_connection_layout.addWidget(self.db_icon_label)

        test_connection_layout.addStretch()

        self.test_connection_button = DataPlotStudioButton("Test Connection", parent=self)
        self.test_connection_button.clicked.connect(self.test_connection)
        test_connection_layout.addWidget(self.test_connection_button)

        self.connection_layout.addRow("", self.test_connection_wrapper)

        self.connection_group.setLayout(self.connection_layout)
        main_layout.addWidget(self.connection_group)

        # Editor grouping with a splitter instead of hardlocked widgets
        self.editors_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Query editor
        query_group = DataPlotStudioGroupBox("SQL Query", parent=self)
        query_layout = QVBoxLayout()
        instructions = (
            "Enter your SQL query below. You can select specific columns and join tables.\n"
            "Supports standard SELECT statements and CTEs."
        )
        self.info_label = QLabel(instructions)
        self.info_label.setWordWrap(True)
        query_layout.addWidget(self.info_label)
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("SELECT * FROM table_name ...")
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
        self.editors_splitter.addWidget(query_group)

        # Schema viewer
        schema_group = DataPlotStudioGroupBox("Database Schema", parent=self)
        schema_layout = QVBoxLayout()

        self.load_schema_button = DataPlotStudioButton("Load Tables and Columns", parent=self)
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
        self.editors_splitter.addWidget(schema_group)

        # Set sizes for splitter. query is larger than schema
        self.editors_splitter.setStretchFactor(0, 3)
        self.editors_splitter.setStretchFactor(1, 2)

        main_layout.addWidget(self.editors_splitter, stretch=1)

        #buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.query_editor.textChanged.connect(self.on_query_changed)

        self.on_db_type_changed("SQLite")
        self.on_query_changed()
    
    def test_connection(self) -> None:
        """Tests the database connection before loading the schema"""
        try:
            self.setCursor(Qt.CursorShape.WaitCursor)
            connection_string = self._build_connection_string()

            # Create an sql engine and attempt a query
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.information(self, "Success", "Connection established")
        
        except ValueError as InputError:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.warning(self, "Input Error", str(InputError))
        except Exception as ConnectionError:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QMessageBox.critical(self, "Connection Failed", f"Could not connect to database:\n{str(ConnectionError)}")

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

        if db_type in ["SQLite", "DuckDB"]:
            db_path = self.file_db_path_input.text().strip()
            if not db_path:
                raise ValueError(f"Please provide a path to the {db_type} database file.")
            
            db_path_abs = str(Path(db_path).resolve())
            prefix = "sqlite" if db_type == "SQLite" else "duckdb"
            #Handle Windows path for sqlalchemy
            if sys.platform == "win32":
                connection_string = f"{prefix}:///{db_path_abs}"
            else:
                connection_string = f"{prefix}:///{db_path_abs}"
        
        else:
            host = self.host_input.text().strip()
            port = self.port_input.text().strip()
            user = self.user_input.text().strip()
            password = self.password_input.text().strip()
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
                "Invalid query (Must be a SELECT statement or WITH clause)",
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
        is_file_db = (db_type in ["SQLite", "DuckDB"])

        #toggle server fields
        self.host_label.setVisible(not is_file_db)
        self.host_input.setVisible(not is_file_db)
        self.port_label.setVisible(not is_file_db)
        self.port_input.setVisible(not is_file_db)
        self.user_label.setVisible(not is_file_db)
        self.user_input.setVisible(not is_file_db)
        self.password_label.setVisible(not is_file_db)
        self.password_input.setVisible(not is_file_db)
        self.dbname_label.setVisible(not is_file_db)
        self.dbname_input.setVisible(not is_file_db)

        #toggle SQLITE fields
        self.file_db_label.setVisible(is_file_db)
        self.file_db_widget.setVisible(is_file_db)

        #set defaults on port and usr
        if db_type == "PostgreSQL":
            self.port_input.setText("5432")
            self.user_input.setText("postgres")
            self.dbname_input.setText("postgres")
        elif db_type == "MySQL":
            self.port_input.setText("3306")
            self.user_input.setText("root")
            self.dbname_input.setText("")
        elif db_type == "DuckDB":
            self.file_db_path_input.setPlaceholderText("Click 'Browse' to select a DuckDB file (.db, .duckdb)")
        elif db_type == "SQLite":
            self.file_db_path_input.setPlaceholderText("Click 'Browse' to select a SQLite file (.db, .sqlite, .sqlite3)")

        # Update the icon
        icon_map = {
            "SQLite": "icons/database_icons/sqlite.svg",
            "DuckDB": "icons/database_icons/duckdb-logo.svg",
            "PostgreSQL": "icons/database_icons/postgresql-inc.svg",
            "MySQL": "icons/database_icons/mysql-3.svg"
        }
        icon_path = icon_map.get(db_type, "")

        if not Path(icon_path).exists():
            icon_path = "icons/menu_bar/database.png"
        
        if Path(icon_path).exists():
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaledToHeight(24, Qt.TransformationMode.SmoothTransformation)
            self.db_icon_label.setPixmap(scaled_pixmap)
            self.db_icon_label.setToolTip(f"{db_type} Database")
        else:
            self.db_icon_label.clear()

    def browse_file_db(self) -> None:
        """Open a file dialog to find a local SQLite database file"""
        current_database_type = self.db_type_combo.currentText()

        filters = "All Files (*)"
        if current_database_type == "SQLite":
            filters = "SQLite Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        elif current_database_type == "DuckDB":
            filters = "DuckDB Files (*.db *.duckdb);;All Files (*)"
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {current_database_type} Database file",
            "",
            filters
        )
        if filepath:
            self.file_db_path_input.setText(filepath)

    def on_accept(self):
        """Validate the input and build connection string before acception"""
        db_type = self.db_type_combo.currentText()
        query = self.query_editor.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a SQL Query")
            return
        
        if not (query.lower().startswith("select") or query.lower().startswith("with")):
            QMessageBox.warning(
                self,
                "Invalid Query Syntax",
                "The SQL query must be a 'SELECT' statement or start with 'WITH'"
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