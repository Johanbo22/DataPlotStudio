from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.dialogs import CreateSubsetDialog, SubsetDataViewer


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QInputDialog, QLabel, QListWidget, QListWidgetItem, QMessageBox, QSplitter, QTextEdit, QVBoxLayout, QWidget



from ui.widgets.AnimatedButton import DataPlotStudioButton


class SubsetManagerDialog(QDialog):
    """Dialog for handling data susbets"""
    plot_subset_requested = pyqtSignal(str)

    def __init__(self, subset_manager, data_handler, parent=None):
        super().__init__(parent)
        self.subset_manager = subset_manager
        self.data_handler = data_handler
        self.setWindowTitle("Data Subsets Tool")
        self.setModal(True)
        self.resize(900, 600)

        self.init_ui()
        print(f"DEBUG: SubsetManager has {len(self.subset_manager.list_subsets())} subsets")
        if self.data_handler.df is not None:
            print("DEBUG: Applying subsets to calculate row counts")
            self.apply_all_subsets()
        else:
            print("DEBUG: No data to apply subsets")

        print("DEBUG: Refreshing the subset list")
        self.refresh_subset_list()

        print(f"DEBUG: QListWidget has {self.subset_list.count()} items")

    def apply_all_subsets(self):
        """Apply all subsets to calculate row counts"""
        print("DEBUG apply_all_subsets: Starting")

        if self.data_handler.df is None:
            print("WARNING apply_all_subsets: No data available")
            return

        if not hasattr(self, 'subset_manager'):
            print("ERROR apply_all_subsets: No subset_manager")
            return

        try:
            subset_names = self.subset_manager.list_subsets()
            print(f"DEBUG apply_all_subsets: Processing {len(subset_names)} subsets")

            for name in subset_names:
                try:
                    print(f"DEBUG apply_all_subsets: Applying subset '{name}'")
                    result_df = self.subset_manager.apply_subset(self.data_handler.df, name)
                    print(f"DEBUG apply_all_subsets: Subset '{name}' has {len(result_df)} rows")
                except Exception as ApplySubsetError:
                    print(f"WARNING apply_all_subsets: Could not apply subset {name}: {str(ApplySubsetError)}")
                    continue

        except Exception as ApplySubsetError:
            print(f"ERROR apply_all_subsets: {str(ApplySubsetError)}")
            import traceback
            traceback.print_exc()

    def init_ui(self):
        """Init ui for the dialog"""
        layout = QVBoxLayout()

        #title
        title = QLabel("Data Subset Creation Tool")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        #info
        info = QLabel(
            "Create named subsets (filtered views) of your data to create unique ways to analysing and visualize your data.\n"
            "Subsets do not modify your original data"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info)

        #main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        #left subset list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Existing Subsets"))

        self.subset_list = QListWidget()
        self.subset_list.itemClicked.connect(self.on_subset_selected)
        left_layout.addWidget(self.subset_list)

        print("DEBUG init_ui: Created subset_list QListWidget")

        # buttons for the list
        list_buttons = QHBoxLayout()

        self.new_btn = DataPlotStudioButton("New Subset", parent=self)
        self.new_btn.clicked.connect(self.create_new_subset)
        list_buttons.addWidget(self.new_btn)

        self.auto_create_btn = DataPlotStudioButton("Auto create subsets by column", parent=self)
        self.auto_create_btn.clicked.connect(self.auto_create_subsets)
        list_buttons.addWidget(self.auto_create_btn)

        left_layout.addLayout(list_buttons)

        splitter.addWidget(left_widget)

        #right subset detials
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.details_group = DataPlotStudioGroupBox("Subset Details", parent=self)
        details_layout = QVBoxLayout()

        #name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_label = QLabel("(Select a Subset)")
        self.name_label.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        details_layout.addLayout(name_layout)

        #description
        details_layout.addWidget(QLabel("Description:"))
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        details_layout.addWidget(self.description_label)

        #stats
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("Rows:"))
        self.rows_label = QLabel("-")
        stats_layout.addWidget(self.rows_label)
        stats_layout.addSpacing(20)
        stats_layout.addWidget(QLabel("Created:"))
        self.created_label = QLabel("-")
        stats_layout.addWidget(self.created_label)
        stats_layout.addStretch()
        details_layout.addLayout(stats_layout)

        #filters
        details_layout.addWidget(QLabel("Filters:"))
        self.filters_text = QTextEdit()
        self.filters_text.setReadOnly(True)
        self.filters_text.setMaximumHeight(150)
        details_layout.addWidget(self.filters_text)

        # Action buttons
        action_buttons = QHBoxLayout()

        self.view_btn = DataPlotStudioButton("View Data", parent=self)
        self.view_btn.clicked.connect(self.view_subset_data)
        self.view_btn.setEnabled(False)
        action_buttons.addWidget(self.view_btn)

        self.plot_btn = DataPlotStudioButton("Plot Subset", parent=self)
        self.plot_btn.clicked.connect(self.plot_subset)
        self.plot_btn.setEnabled(False)
        action_buttons.addWidget(self.plot_btn)

        self.edit_btn = DataPlotStudioButton("Edit", parent=self)
        self.edit_btn.clicked.connect(self.edit_subset)
        self.edit_btn.setEnabled(False)
        action_buttons.addWidget(self.edit_btn)

        self.delete_btn = DataPlotStudioButton("Delete", parent=self)
        self.delete_btn.clicked.connect(self.delete_subset)
        self.delete_btn.setEnabled(False)
        action_buttons.addWidget(self.delete_btn)

        details_layout.addLayout(action_buttons)

        self.details_group.setLayout(details_layout)
        right_layout.addWidget(self.details_group)

        right_layout.addStretch()

        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])

        layout.addWidget(splitter)

        # bottom buttons [lmao 
        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()

        close_btn = DataPlotStudioButton("Close", parent=self)
        close_btn.clicked.connect(self.accept)
        bottom_buttons.addWidget(close_btn)

        layout.addLayout(bottom_buttons)
        self.setLayout(layout)

        print("DEBUG init_ui: UI initialization complete")

    def refresh_subset_list(self):
        """Refreshes the list of subsets"""
        print("DEBUG: resfresh_subset_list: Starting")
        print(f"DEBUG: refresh_subset_list: subset_list widget exists: {hasattr(self, "subset_list")}")

        if not hasattr(self, "subset_list"):
            print("ERROR: subset_list_widget not found")
            return

        self.subset_list.clear()
        print("DEBUG: refresh_subset_list: Cleared the list widget")

        subset_names = self.subset_manager.list_subsets()
        print(f"DEBUG refresh_subset_list: Found {len(subset_names)} subsets: {subset_names}")

        if not subset_names:
            placeholder = QListWidgetItem("(No subsets created yet)")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.subset_list.addItem(placeholder)
            print("DEBUG: refresh_subset_list: Added placeholder for empty list")
            return

        for name in subset_names:
            try:
                subset = self.subset_manager.get_subset(name)
                if not subset:
                    print(f"WARNING: Subset '{name}' returned None from get_subset()")
                    continue

                row_text = f"{subset.row_count} rows" if subset.row_count > 0 else "? rows"
                item_text = f"{name} ({row_text})"
                print(f"DEBUG: refresh_subset_list: Adding item: {item_text}")

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.subset_list.addItem(item)
                print(f"DEBUG refresh_subset_list: Addded: {name}")

            except Exception as RefreshSubsetToListError:
                print(f"ERROR adding subset {name} to list: {str(RefreshSubsetToListError)}")
                import traceback
                traceback.print_exc()
                continue

        final_count = self.subset_list.count()
        print(f"DEBUG refresh_subset_list: Final item count: {final_count}")

    def on_subset_selected(self, item):
        """Subset selection"""
        # Check if item is the placeholder
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        subset = self.subset_manager.get_subset(name)

        if not subset:
            QMessageBox.warning(self, "Error", f"Subset '{name}' not found")
            return

        # Update UI with subset information
        self.name_label.setText(name)
        self.description_label.setText(subset.description or "No Description")
        self.rows_label.setText(str(subset.row_count) if subset.row_count > 0 else "?")
        self.created_label.setText(subset.created_at.strftime("%Y-%m-%d %H:%M"))

        # Format filters
        filters_text = f"Logic: {subset.logic}\n\nFilters:\n"
        for i, f in enumerate(subset.filters, 1):
            filters_text += f"{i}. {f['column']} {f['condition']} '{f['value']}'\n"

        self.filters_text.setText(filters_text)

        # Enable buttons
        self.view_btn.setEnabled(True)
        self.plot_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def create_new_subset(self):
        """Create a new subset"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        dialog = CreateSubsetDialog(
            self.data_handler.df.columns.tolist(),
            self
        )

        if dialog.exec():
            config = dialog.get_config()
            try:
                self.subset_manager.create_subset(
                    name=config["name"],
                    description=config["description"],
                    filters=config["filters"],
                    logic=config["logic"]
                )

                #apply 
                self.subset_manager.apply_subset(self.data_handler.df, config["name"])

                self.refresh_subset_list()
                QMessageBox.information(self, "Success", f"Subset '{config['name']}' created")
            except ValueError as CreateNewSubsetError:
                QMessageBox.warning(self, "Error", {str(CreateNewSubsetError)})

    def auto_create_subsets(self):
        """Auto create subsets based on unique values in a column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        column, ok = QInputDialog.getItem(
            self,
            "Auto-Create Subsets",
            "Select column to split by:",
            self.data_handler.df.columns.tolist(),
            0,
            False
        )

        if ok and column:
            unique_count = self.data_handler.df[column].nunique()

            reply = QMessageBox.question(
                self,
                "Confirm",
                f"This will create {unique_count} subsets (one for each unique value in '{column}').\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    created = self.subset_manager.create_subset_from_unique_values(
                        self.data_handler.df,
                        column
                    )

                    #apply 
                    for name in created:
                        self.subset_manager.apply_subset(self.data_handler.df, name)

                    self.refresh_subset_list()
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Created {len(created)} subsets from column '{column}'"
                    )
                except Exception as AutoCreateSubsetError:
                    QMessageBox.critical(self, "Error", str(AutoCreateSubsetError))

    def view_subset_data(self):
        """View the filtered data for a selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        try:
            subset_df = self.subset_manager.apply_subset(self.data_handler.df, name)

            #show in new dialog
            viewer = SubsetDataViewer(subset_df, name, self)
            viewer.exec()
        except Exception as ViewSubsetDataError:
            QMessageBox.critical(self, "Error", str(ViewSubsetDataError))

    def plot_subset(self):
        """Switch to plot tab with subset data active"""
        item = self.subset_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Please select a subset you wish to visualize")
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        if not name:
            return

        self.plot_subset_requested.emit(name)
        self.accept()

    def edit_subset(self):
        """Edit the selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        subset = self.subset_manager.get_subset(name)

        dialog = CreateSubsetDialog(
            self.data_handler.df.columns.tolist(),
            self,
            existing_subset=subset
        )

        if dialog.exec():
            config = dialog.get_config()
            try:
                self.subset_manager.update_subset(
                    name=name,
                    description=config["description"],
                    filters=config["filters"],
                    logic=config["logic"]
                )

                # apply agian
                self.subset_manager.apply_subset(self.data_handler.df, name, use_cache=False)

                self.refresh_subset_list()
                self.on_subset_selected(item)
                QMessageBox.information(self, "Success", f"Subset '{name}' updated")
            except Exception as EditSubsetError:
                QMessageBox.warning(self, "Error", str(EditSubsetError))

    def delete_subset(self):
        """Delete the selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return

        name = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete subset '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.subset_manager.delete_subset(name)
            self.refresh_subset_list()

            # Clear details
            self.name_label.setText("(Select a subset)")
            self.description_label.setText("")
            self.rows_label.setText("-")
            self.created_label.setText("-")
            self.filters_text.clear()

            # Disable buttons
            self.view_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)