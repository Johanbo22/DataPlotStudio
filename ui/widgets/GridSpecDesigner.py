from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QMenu
from PyQt6.QtCore import pyqtSignal, Qt, QEvent, QPoint
from PyQt6.QtGui import QKeyEvent, QColor, QBrush, QFont

from typing import List, Tuple, Optional

from ui.theme import ThemeColors
from ui.widgets import DataPlotStudioSpinBox, DataPlotStudioButton

class GridSpecDesignerWidget(QWidget):
    """
    A visual widget to design GridSpec layouts.
    Uses a QTableWidget to act as an grid builder.
    """
    
    layout_applied = pyqtSignal(int, int, list)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("GridSpecDesignerWidget")
        self._defined_spans: List[Tuple[int, int, int, int]] = []
        self._sharex: bool = False
        self._sharey: bool = False
        
        self._init_ui()
        self._connect_signals()
        self._update_grid_data()
        
    def _init_ui(self) -> None:
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.controls_layout = QHBoxLayout()
        self.rows_spin = DataPlotStudioSpinBox()
        self.rows_spin.setObjectName("gridRowsSpinBox")
        self.rows_spin.setRange(1, 10)
        self.rows_spin.setValue(2)
        
        self.cols_spin = DataPlotStudioSpinBox()
        self.cols_spin.setObjectName("gridColsSpinBox")
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(2)
        
        row_label = QLabel("Grid Rows:")
        row_label.setProperty("styleClass", "settings_label")
        col_label = QLabel("Grid Columns:")
        col_label.setProperty("styleClass", "settings_label")

        self.controls_layout.addWidget(row_label)
        self.controls_layout.addWidget(self.rows_spin)
        self.controls_layout.addWidget(col_label)
        self.controls_layout.addWidget(self.cols_spin)
        self.controls_layout.addStretch()
        
        self.grid_table = QTableWidget()
        self.grid_table.setObjectName("layoutGridTable")
        self.grid_table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)
        self.grid_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grid_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.grid_table.setShowGrid(True)
        self.grid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.horizontalHeader().setVisible(False)
        self.grid_table.verticalHeader().setVisible(False)
        self.grid_table.setMinimumHeight(150)
        
        self.grid_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.actions_layout = QHBoxLayout()
        self.merge_cells_btn = DataPlotStudioButton("Add / Merge Plot")
        self.merge_cells_btn.setObjectName("mergeCellsBtn")
        self.merge_cells_btn.setToolTip("Create a new plot or merge existing ones in the selected area.")
        
        self.remove_cells_btn = DataPlotStudioButton("Remove Plot")
        self.remove_cells_btn.setObjectName("removeCellsBtn")
        self.remove_cells_btn.setToolTip("Remove the plot from the selected area, leaving an empty space.")
        
        self.reset_grid_btn = DataPlotStudioButton("Reset Grid")
        self.reset_grid_btn.setObjectName("resetGridBtn")
        
        self.apply_layout_btn = DataPlotStudioButton("Apply Layout", base_color_hex=ThemeColors.MainColor)
        self.apply_layout_btn.setObjectName("applyDashboardLayoutBtn")
        self.apply_layout_btn.setProperty("actionType", "primary")

        self.actions_layout.addWidget(self.merge_cells_btn)
        self.actions_layout.addWidget(self.remove_cells_btn)
        self.actions_layout.addWidget(self.reset_grid_btn)
        self.actions_layout.addStretch()
        self.actions_layout.addWidget(self.apply_layout_btn)

        self.main_layout.addLayout(self.controls_layout)
        self.main_layout.addWidget(self.grid_table)
        self.main_layout.addLayout(self.actions_layout)
        
        self.setLayout(self.main_layout)
    
    def _connect_signals(self) -> None:
        self.rows_spin.valueChanged.connect(self._update_grid_data)
        self.cols_spin.valueChanged.connect(self._update_grid_data)
        self.merge_cells_btn.clicked.connect(self._merge_selected)
        self.remove_cells_btn.clicked.connect(self._remove_selected)
        self.reset_grid_btn.clicked.connect(self._update_grid_data)
        self.apply_layout_btn.clicked.connect(self._emit_layout)
        
        self.grid_table.cellDoubleClicked.connect(self._handle_double_click)
        self.grid_table.customContextMenuRequested.connect(self._show_context_menu)
        
        self.grid_table.installEventFilter(self)
        
    def eventFilter(self, source: QWidget, event: QEvent) -> bool:
        if source is self.grid_table and event.type() == QEvent.Type.KeyPress:
            key_event = getattr(event, "key", lambda: None)()
            
            if key_event in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                self._remove_selected()
                return True
            elif key_event in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._merge_selected()
                return True
        return super().eventFilter(source, event)
    
    def _handle_double_click(self, row: int, col: int) -> None:
        """
        Handles the double clicking on a cell to change 
        its state from empty to plot and vice-versa
        """
        span_to_remove = None
        
        for span in self._defined_spans:
            r_start, r_end, c_start, c_end = span
            if r_start <= row < r_end and c_start <= col < c_end:
                span_to_remove = span
                break
        if span_to_remove:
            self._defined_spans.remove(span_to_remove)
        else:
            self._defined_spans.append((row, row + 1, col, col + 1))
        self._redraw_table()
        
    def _show_context_menu(self, position: QPoint) -> None:
        menu = QMenu(self)
        
        merge_action = menu.addAction("Add / Merge Selected")
        remove_action = menu.addAction("Remove Selected")
        menu.addSeparator()
        reset_action = menu.addAction("Reset Grid")
        
        merge_action.triggered.connect(self._merge_selected)
        remove_action.triggered.connect(self._remove_selected)
        reset_action.triggered.connect(self._update_grid_data)
        
        menu.exec(self.grid_table.mapToGlobal(position))
    
    def _update_grid_data(self) -> None:
        """
        Rebuilds the table structure to reflect changes in rows/cols
        """
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        self._defined_spans.clear()
        for r in range(rows):
            for c in range(cols):
                self._defined_spans.append((r, r + 1, c, c + 1))
        self._redraw_table()
    
    def set_shared_axes(self, sharex: bool, sharey: bool) -> None:
        self._sharex = sharex
        self._sharey = sharey
        
        self.grid_table.setProperty("sharex", sharex)
        self.grid_table.setProperty("sharey", sharey)
        self.grid_table.style().unpolish(self.grid_table)
        self.grid_table.style().polish(self.grid_table)
        
        self._redraw_table()
    
    def _redraw_table(self) -> None:
        """Paints the table using the internal span state, enforcing numeric ordering."""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        
        self.grid_table.setRowCount(rows)
        self.grid_table.setColumnCount(cols)
        self.grid_table.clearSpans()
        self.grid_table.clearContents()
        
        for r in range(rows):
            for c in range(cols):
                empty_item = QTableWidgetItem("Empty")
                empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_item.setToolTip(f"Empty Space.\nDouble click to add a new plot here")
                self.grid_table.setItem(r, c, empty_item)

        self._defined_spans.sort(key=lambda x: (x[0], x[2]))
        plot_palette = [
            QColor(58, 134, 255, 40),  
            QColor(46, 196, 182, 40),  
            QColor(155, 93, 229, 40),  
            QColor(243, 167, 18, 40), 
            QColor(231, 29, 54, 40),   
            QColor(0, 187, 249, 40)    
        ]
        bold_font = QFont()
        bold_font.setBold(True)

        for idx, (r_start, r_end, c_start, c_end) in enumerate(self._defined_spans):
            has_x = not self._sharex or r_end == rows
            has_y = not self._sharey or c_start == 0
            
            item = QTableWidgetItem()
            bg_color = plot_palette[idx % len(plot_palette)]
            item.setBackground(QBrush(bg_color))
            
            row_span = r_end - r_start
            col_span = c_end - c_start
            span_desc = f"{row_span}x{col_span} block" if (row_span > 1 or col_span > 1) else "1x1 block"
            axis_desc = f"Active Axes: {'X ' if has_x else ''}{'& Y' if has_y else ''}{'None (Fully Shared)' if not has_x and not has_y else ''}"
            item.setToolTip(f"Plot {idx + 1} ({span_desc})\n{axis_desc}\nDouble-click to remove this plot.")
            
            self.grid_table.setItem(r_start, c_start, item)
            
            cell_widget = QLabel(f"Plot {idx + 1}")
            cell_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            
            border_css = []
            if has_x:
                border_css.append("border-bottom: 3px solid #88B6FF;")
            if has_y:
                border_css.append("border-left: 3px solid #88B6FF;")
                
            cell_widget.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    font-weight: bold;
                    color: palette(text);
                    {' '.join(border_css)}
                }}
            """)
            self.grid_table.setCellWidget(r_start, c_start, cell_widget)
                        
            if row_span > 1 or col_span > 1:
                self.grid_table.setSpan(r_start, c_start, row_span, col_span)
    
    def _merge_selected(self) -> None:
        """Consumes selected cells and combines them into a single subplot block."""
        selected_ranges = self.grid_table.selectedRanges()
        if not selected_ranges:
            return
        
        selection = selected_ranges[0]
        r_start = selection.topRow()
        r_end = selection.bottomRow() + 1
        c_start = selection.leftColumn()
        c_end = selection.rightColumn() + 1
        
        new_spans = []
        for span in self._defined_spans:
            sr_start, sr_end, sc_start, sc_end = span
            if not (sr_start >= r_end or sr_end <= r_start or sc_start >= c_end or sc_end <= c_start):
                continue
            new_spans.append(span)

        new_spans.append((r_start, r_end, c_start, c_end))
        self._defined_spans = new_spans
        self._redraw_table()
    
    def _remove_selected(self) -> None:
        selected_ranges = self.grid_table.selectedRanges()
        if not selected_ranges:
            return
        
        selection = selected_ranges[0]
        r_start = selection.topRow()
        r_end = selection.bottomRow() + 1
        c_start = selection.leftColumn()
        c_end = selection.rightColumn() + 1
        
        new_spans = []
        for span in self._defined_spans:
            sr_start, sr_end, sc_start, sc_end = span
            if (sr_start >= r_end or sr_end <= r_start or sc_start >= c_end or sc_end <= c_start):
                new_spans.append(span)
        
        self._defined_spans = new_spans
        self._redraw_table()
    
    def _emit_layout(self) -> None:
        if not self._defined_spans:
            QMessageBox.warning(
                self,
                "Invalid Layout",
                "Cannot apply an empty layout. Please ensure at least one plot is defined in the grid"
            )
            return
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        self.layout_applied.emit(rows, cols, self._defined_spans.copy())