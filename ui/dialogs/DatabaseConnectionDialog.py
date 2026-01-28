from tkinter import N
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox


from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QThreadPool, QSettings
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QTextEdit, QVBoxLayout, QWidget, QStyle, QTreeWidget, QTreeWidgetItem, QSplitter, QRadioButton, QButtonGroup, QInputDialog

from ui.widgets.AnimatedRadioButton import DataPlotStudioRadioButton
from ui.workers import TestConnectionWorker
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
        self.setWindowIcon(QIcon("icons/menu_bar/database.svg"))
        self.setMinimumWidth(900)
        self.resize(100, 600)

        self.details = {}

        self.settings = QSettings("DataPlotStudio", "DatabaseProfiles")
        self.threadpool = QThreadPool.globalInstance()

        main_layout = QVBoxLayout(self)

        # Profile selection
        profiles_group = DataPlotStudioGroupBox("Saved Connections", parent=self)
        profiles_layout = QHBoxLayout()

        profiles_layout.addWidget(QLabel("Profile:"))
        self.profiles_combo = DataPlotStudioComboBox()
        self.populate_profiles()
        self.profiles_combo.currentIndexChanged.connect(self.load_profile)
        profiles_layout.addWidget(self.profiles_combo, 1)

        self.save_profile_button = DataPlotStudioButton("Save", parent=self)
        self.save_profile_button.setToolTip("Save the current connection details")
        self.save_profile_button.clicked.connect(self.save_profile)
        profiles_layout.addWidget(self.save_profile_button)

        self.delete_profile_button = DataPlotStudioButton("Delete", parent=self)
        self.delete_profile_button.setToolTip("Delete selected profile")
        self.delete_profile_button.clicked.connect(self.delete_profile)
        profiles_layout.addWidget(self.delete_profile_button)

        profiles_group.setLayout(profiles_layout)
        main_layout.addWidget(profiles_group)

        # Connection mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Connection Mode:"))
        self.mode_group = QButtonGroup(self)

        self.mode_builder_radio = DataPlotStudioRadioButton("Connection Builder")
        self.mode_builder_radio.setChecked(True)
        self.mode_builder_radio.toggled.connect(self.toggle_connection_mode)
        self.mode_group.addButton(self.mode_builder_radio)
        mode_layout.addWidget(self.mode_builder_radio)

        self.mode_uri_radio = DataPlotStudioRadioButton("Raw Connection URI")
        self.mode_uri_radio.toggled.connect(self.toggle_connection_mode)
        self.mode_group.addButton(self.mode_uri_radio)
        mode_layout.addWidget(self.mode_uri_radio)

        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        #type selection
        db_type_layout = QHBoxLayout()
        db_type_layout.addWidget(QLabel("Database Type:"))
        self.db_type_combo = DataPlotStudioComboBox()
        self.db_type_combo.addItems(["SQLite","DuckDB", "PostgreSQL", "MySQL"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        db_type_layout.addWidget(self.db_type_combo)
        main_layout.addLayout(db_type_layout)
        self.db_type_container = db_type_layout

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

        #raw uri
        self.uri_label = QLabel("Connection URI:")
        self.uri_input = DataPlotStudioLineEdit()
        self.uri_input.setPlaceholderText("dialect+driver://username:password@host:port/database")
        self.uri_input.setVisible(False)
        self.uri_label.setVisible(False)
        self.connection_layout.addRow(self.uri_label, self.uri_input)

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
            self.test_connection_button.setEnabled(False)
            self.test_connection_button.setText("Testing...")
            self.db_icon_label.setText("⌛") # TODO: Add a better icon. using this as placeholder

            connection_string = self._build_connection_string()

            worker = TestConnectionWorker(connection_string)
            worker.signals.finished.connect(self.on_test_connection_success)
            worker.signals.error.connect(self.on_test_connection_error)

            self.threadpool.start(worker)
        
        except ValueError as InputError:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.test_connection_button.setEnabled(True)
            self.test_connection_button.setText("Test Connection")
            self.db_icon_label.clear()
            QMessageBox.warning(self, "Input Error", str(InputError))

    def on_test_connection_success(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.test_connection_button.setEnabled(True)
        self.test_connection_button.setText("Test Connection")
        self.db_icon_label.setToolTip("Connected")
        QMessageBox.information(self, "Success", "Connection established")
    
    def on_test_connection_error(self, error):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.test_connection_button.setEnabled(True)
        self.test_connection_button.setText("Test Connection")
        QMessageBox.critical(self, "Connection Failed", f"Could not connect to the database:\n{str(error)}")

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
        # URI mode
        if self.mode_uri_radio.isChecked():
            uri = self.uri_input.text().strip()
            if not uri:
                raise ValueError("Please provide a valid Connection URI")
            return uri

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
        if self.mode_uri_radio.isChecked():
            return

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
            icon_path = "icons/menu_bar/database.svg"
        
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
    
    def toggle_connection_mode(self):
        """Switches the UI states"""
        is_uri_mode = self.mode_uri_radio.isChecked()

        self.uri_label.setVisible(is_uri_mode)
        self.uri_input.setVisible(is_uri_mode)

        builder_visible = not is_uri_mode

        self.db_type_combo.setVisible(builder_visible)

        if is_uri_mode:
            self.host_label.setVisible(False)
            self.host_input.setVisible(False)
            self.port_label.setVisible(False)
            self.port_input.setVisible(False)
            self.user_label.setVisible(False)
            self.user_input.setVisible(False)
            self.password_label.setVisible(False)
            self.password_input.setVisible(False)
            self.dbname_label.setVisible(False)
            self.dbname_input.setVisible(False)
            self.file_db_label.setVisible(False)
            self.file_db_widget.setVisible(False)
        else:
            self.on_db_type_changed(self.db_type_combo.currentText())
    
    def populate_profiles(self):
        self.profiles_combo.blockSignals(True)
        self.profiles_combo.clear()
        self.profiles_combo.addItem("Select a profile...", None)

        self.settings.beginGroup("DatabaseProfiles")
        profiles = self.settings.childGroups()
        self.settings.endGroup()

        for profile in profiles:
            self.profiles_combo.addItem(profile, profile)
        self.profiles_combo.blockSignals(False)
    
    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name")
        if ok and name:
            if not name.strip():
                QMessageBox.warning(self, "Error", "Profile name cannot be empty")
                return
            
            is_uri = self.mode_uri_radio.isChecked()
            data = {
                "mode": "uri" if is_uri else "builder",
                "uri": self.uri_input.text(),
                "db_type": self.db_type_combo.currentText(),
                "host": self.host_input.text(),
                "port": self.port_input.text(),
                "user": self.user_input.text(),
                "password": self.password_input.text(),
                "dbname": self.dbname_input.text(),
                "file_path": self.file_db_path_input.text()
            }

            self.settings.beginGroup("DatabaseProfiles")
            self.settings.beginGroup(name)
            for key, val in data.items():
                self.settings.setValue(key, val)
            self.settings.endGroup()
            self.settings.endGroup()

            self.populate_profiles()
            index = self.profiles_combo.findText(name)
            if index >= 0:
                self.profiles_combo.setCurrentIndex(index)
            
            QMessageBox.information(self, "Saved", f"Profile '{name}' saved")
    
    def load_profile(self):
        """Load the selected profile"""
        name = self.profiles_combo.currentData()
        if not name:
            return
        
        self.settings.beginGroup("DatabaseProfiles")
        self.settings.beginGroup(name)

        mode = self.settings.value("mode", "builder")

        if mode == "uri":
            self.mode_uri_radio.setChecked(True)
            self.uri_input.setText(self.settings.value("uri", ""))
        else:
            self.mode_builder_radio.setChecked(True)
            db_type = self.settings.value("db_type", "SQLite")
            index = self.db_type_combo.findText(db_type)
            if index >= 0:
                self.db_type_combo.setCurrentIndex(index)
            
            self.host_input.setText(self.settings.value("host", ""))
            self.port_input.setText(self.settings.value("port", ""))
            self.user_input.setText(self.settings.value("user", ""))
            self.password_input.setText(self.settings.value("password", ""))
            self.dbname_input.setText(self.settings.value("dbname", ""))
            self.file_db_path_input.setText(self.settings.value("file_path", ""))

            self.on_db_type_changed(db_type)
        
        self.settings.endGroup()
        self.settings.endGroup()
    
    def delete_profile(self):
        """Delete current profile"""
        name = self.profiles_combo.currentData()
        if not name:
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete profile '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.settings.beginGroup("DatabaseProfiles")
            self.settings.remove(name)
            self.settings.endGroup()
            self.populate_profiles()