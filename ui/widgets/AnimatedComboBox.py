from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QComboBox, QToolButton, QCompleter
from core.resource_loader import get_resource_path
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioComboBox(HoverFocusAnimationMixin, QComboBox):
    """A Combobox with animated borders and arrow
    Search enabled by a QSortFilterProxyModel
    Clear button
    Selected states and invalid states  highlighted
    """
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        HoverFocusAnimationMixin.__init__(self)
        
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = self.completer()
        if completer:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.popup().setStyleSheet("""
                QListView { 
                    background-color: white; 
                    color: #333333;
                    selection-background-color: #e0e0e0;
                    selection-color: #000000; 
                }
            """)
        
        # Setup search line
        self.lineEdit().setPlaceholderText("Select or search...")
        
        # Setup a clear button
        self._clear_button: QToolButton = QToolButton(self)
        self._clear_button.setIcon(QIcon(get_resource_path("icons/clean.svg"))) # TODO: Update this icon
        self._clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_button.setStyleSheet("border: none; background: transparent; padding: 0px;")
        self._clear_button.setToolTip("Clear selection")
        self._clear_button.clicked.connect(self.clear_selection)
        self._clear_button.hide()

        self._update_stylesheet(self._base_border_color)
    
    def clear_selection(self) -> None:
        """Resets the combobox to an unselected state"""
        self.setCurrentIndex(-1)
        self.setEditText("")
    
    def resizeEvent(self, event) -> None:
        """Positions the clear button inside the right side of the widget frame"""
        super().resizeEvent(event)
        button_size: QSize = self._clear_button.sizeHint()
        x_pos: int = self.width() - button_size.width() - 25
        y_pos: int = (self.height() - button_size.height()) // 2
        self._clear_button.move(x_pos, y_pos)

    def _update_stylesheet(self, color: QColor) -> None:
        arrow_icon_path = get_resource_path("icons/ui_styling/arrow-down-to-line.svg").replace("\\", "/")

        self.setStyleSheet(f"""
            QComboBox {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 35px 1px 3px;
                min-width: 6em;
                background-color: white;
                color: #333333;
            }}
            QComboBox QLineEdit {{
                background: transparent;
                border: none;
            }}
            QComboBox:item:selected:!enabled, 
            QComboBox[currentIndex="-1"] {{
                color: #888888;
                font-style: italic;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: {color.name()};
                border-left-style: solid; 
                border-top-right-radius: 3px; 
                border-bottom-right-radius: 3px;
                background-color: #f0f0f0;
            }}
            QComboBox::drop-down:hover {{
                background-color: #e0e0e0;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_icon_path});
                width: 9px;
                height: 9px;
            }}
            QComboBox:on {{ 
                border: 1.5px solid {self._focus_border_color.name()};
            }}
        """)

    # an override for combobox
    def enterEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._hover_border_color)
        if self.currentIndex() != -1:
            self._clear_button.show()
        QComboBox.enterEvent(self, event)
    
    def leaveEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._base_border_color)
        if not self._clear_button.underMouse():
            self._clear_button.hide()
        QComboBox.leaveEvent(self, event)
    
    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if not self.view().isVisible():
            if self.underMouse():
                self._animate_to(self._hover_border_color)
            else:
                self._animate_to(self._base_border_color)
        if event is not None:
            QComboBox.focusOutEvent(self, event)

    def showPopup(self):
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().showPopup()

    def hidePopup(self):
        super().hidePopup()
        self._is_focussed = False
        self.focusOutEvent(None)