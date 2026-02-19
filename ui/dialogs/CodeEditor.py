from ui.LineNumberArea import LineNumberArea


from PyQt6.QtCore import QRect, Qt, QStringListModel
from PyQt6.QtGui import QColor, QFont, QPainter, QTextCursor, QTextFormat, QAction, QKeySequence, QKeyEvent
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QCompleter, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QWidget



class CodeEditor(QPlainTextEdit):
    """Custom texedit widget that serves as a code editor"""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.lineNumberArea: LineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        # Initialize the autocompleter
        self.completer: QCompleter | None = None
        self.initCompleter()
        
        # Initialize find and replace
        self.find_replace_dialog = None
        find_action = QAction("Find/Replace", self)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        find_action.triggered.connect(self.showFindReplaceDialog)
        self.addAction(find_action)

        #font
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

    def lineNumberAreaWidth(self) -> int:
        digits = 1
        max_value: int = max(1, self.blockCount())
        while max_value >= 10:
            max_value //= 10
            digits += 1

        space: int = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _) -> None:
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy) -> None:
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr: QRect = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#2b2b2b"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#808080"))
                painter.setFont(self.font())
                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#323232")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)
    
    def initCompleter(self):
        """Sets up the QCompleter for Python keywords and builtins"""
        self.completer = QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)
        
        try:
            from resources.autocomplete_keywords import AUTOCOMPLETE_KEYWORDS
            keywords = AUTOCOMPLETE_KEYWORDS
        except ImportError:
            print("Warning:_Could not import autocomplete_keywords. Using default")
            keywords = [
                "def", "class", "if", "else", "elif", "while", "for", "in", "return", 
                "try", "except", "import", "from", "as", "True", "False", "None", 
                "and", "or", "not", "break", "continue", "pass", "lambda", "with", 
                "is", "global", "raise", "yield", "print", "range", "len", "list", 
                "dict", "set", "str", "int", "float", "bool", "super", "__init__",
                "self", "None", "open", "zip", "enumerate", "isinstance"
            ]
        model = QStringListModel(keywords, self.completer)
        self.completer.setModel(model)
    
    def insertCompletion(self, completion):
        """Inserts the selected completion into text"""
        if self.completer.widget() != self:
            return
        
        text_cursor = self.textCursor()
        # calculate how manuy characters we must ignore that has already been tuyped
        extra = len(completion) - len(self.completer.completionPrefix())
        
        # Dont replace the hwole word if typing in the middle
        # complete at end
        # and then move cursor to end position and insert suffix
        text_cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
        text_cursor.insertText(completion[-extra:])
        self.setTextCursor(text_cursor)
        
    def textUnderCursor(self) -> str:
        """Returns the word under the cursor"""
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def startCompleter(self):
        """Trigger the completer popup"""
        if self.completer:
            self.handleCompleterUpdate(force=True)

    def handleCompleterUpdate(self, force: bool = False):
        """updates the completer prefix and shows the completion popup"""
        if not self.completer:
            return
        
        completionPrefix = self.textUnderCursor()
        
        # do not force the popup if 0 or 1 characters is typed
        # only force if keysequence is requested
        if not force and len(completionPrefix) < 1:
            self.completer.popup().hide()
            return
        
        if completionPrefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
        
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect)
    
    def showFindReplaceDialog(self):
        try:
            from ui.dialogs.FindReplaceDialog import FindReplaceDialog
            
            if not self.find_replace_dialog:
                self.find_replace_dialog = FindReplaceDialog(self)
            
            self.find_replace_dialog.show()
            self.find_replace_dialog.activateWindow()
            self.find_replace_dialog.raise_()
            
        except Exception as e:
            print(f"Error opening Find/Replace: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Could not open Find/Replace:\n{e}")
    
    def indentSelection(self, cursor: QTextCursor) -> None:
        """Indents the currently selected text blocks by 4 spaces"""
        global FOUR_SPACES
        FOUR_SPACES = "    "
        try:
            has_selection: bool = cursor.hasSelection()
            start_pos: int = cursor.selectionStart()
            end_pos: int = cursor.selectionEnd()
            
            cursor.setPosition(start_pos)
            start_block: int = cursor.blockNumber()
            cursor.setPosition(end_pos)
            end_block: int = cursor.blockNumber()
            
            if has_selection and cursor.positionInBlock() == 0 and end_block > start_block:
                end_block -= 1
            
            cursor.beginEditBlock()
            for i in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(i)
                cursor.setPosition(block.position())
                cursor.insertText(FOUR_SPACES)
            cursor.endEditBlock()
            
            if has_selection:
                cursor.setPosition(self.document().findBlockByNumber(start_block).position())
                cursor.setPosition(self.document().findBlockByNumber(end_block).position(), QTextCursor.MoveMode.KeepAnchor)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            else:
                cursor.setPosition(start_pos + 4)
            self.setTextCursor(cursor)
        except Exception as e:
            print(f"CodeEditor Indent Error: {e}")
    
    def unindentSelection(self, cursor: QTextCursor) -> None:
        """Unindents the currently selected block by up to four space"""
        try:
            has_selection: bool = cursor.hasSelection()
            start_pos: int = cursor.selectionStart()
            end_pos: int = cursor.selectionEnd()
            
            cursor.setPosition(start_pos)
            start_block: int = cursor.blockNumber()
            cursor.setPosition(end_pos)
            end_block: int = cursor.blockNumber()

            if cursor.positionInBlock() == 0 and end_block > start_block:
                end_block -= 1
            
            cursor.beginEditBlock()
            removed_from_start: int = 0
            for i in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(i)
                cursor.setPosition(block.position())
                block_text: str = block.text()
                
                spaces_to_remove: int = 0
                if block_text.startswith(FOUR_SPACES):
                    spaces_to_remove = 4
                elif block_text.startswith("\t"):
                    spaces_to_remove = 1
                else:
                    for char in block_text[:4]:
                        if char == " ":
                            spaces_to_remove += 1
                        else:
                            break
                            
                if spaces_to_remove > 0:
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, spaces_to_remove)
                    cursor.removeSelectedText()
                    if i == start_block:
                        removed_from_start = spaces_to_remove
                        
            cursor.endEditBlock()
            if has_selection:
                cursor.setPosition(self.document().findBlockByNumber(start_block).position())
                cursor.setPosition(self.document().findBlockByNumber(end_block).position(), QTextCursor.MoveMode.KeepAnchor)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            else:
                new_pos: int = max(self.document().findBlockByNumber(start_block).position(), start_pos - removed_from_start)
                cursor.setPosition(new_pos)
                
            self.setTextCursor(cursor)
        except Exception as e:
            print(f"CodeEditor Unindent Error: {e}")
    
    def keyPressEvent(self, event: QKeyEvent):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                event.ignore()
                return
        
        is_shortcut = (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space)
        if is_shortcut:
            self.startCompleter()
            return
        
        cursor = self.textCursor()
        text = event.text()

        pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        closing_chars = {')', ']', '}', '"', "'"}

        #tabs
        if event.key() == Qt.Key.Key_Tab:
            if cursor.hasSelection():
                self.indentSelection(cursor)
            else:
                cursor.insertText(FOUR_SPACES)
            return
        #backtab
        if event.key() == Qt.Key.Key_Backtab:
            self.unindentSelection(cursor)
            return
        #auto indent on enter
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            block = cursor.block()
            line_text = block.text()

            indentation = ""
            for char in line_text:
                if char == " ": indentation += " "
                elif char == "\t": indentation += "    "
                else: break

            if line_text.rstrip().endswith(":"):
                indentation += "    "
            #Input:(Enter)
            # Output: {
            #             |
            #         }
            pos = cursor.positionInBlock()
            if pos > 0 and pos < len(line_text):
                char_before = line_text[pos-1]
                char_after = line_text[pos]
                if char_before in "{[(" and char_after in "}])":
                    super().keyPressEvent(event)
                    self.insertPlainText(indentation)
                    cursor_pos = self.textCursor().position()
                    self.insertPlainText("\n" + indentation[:-4] if len(indentation)>=4 else "\n")

                    new_cursor = self.textCursor()
                    new_cursor.setPosition(cursor_pos)
                    self.setTextCursor(new_cursor)
                    return

            super().keyPressEvent(event)
            self.insertPlainText(indentation)
            return

        #backspace
        if event.key() == Qt.Key.Key_Backspace:
            pos = cursor.position()
            doc = self.document()
            if pos > 0 and pos < doc.characterCount() - 1:
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                char_before = cursor.selectedText()
                cursor.clearSelection()

                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                char_after = cursor.selectedText()
                cursor.clearSelection()
                cursor.setPosition(pos)

                if char_before in pairs and pairs[char_before] == char_after:
                    cursor.deleteChar()

            super().keyPressEvent(event)
            return

        #typeover
        if text in closing_chars:
            pos = cursor.position()
            block_text = cursor.block().text()
            pos_in_block = cursor.positionInBlock()

            if pos_in_block < len(block_text):
                char_after = block_text[pos_in_block]
                if char_after == text:
                    cursor.movePosition(QTextCursor.MoveOperation.Right)
                    self.setTextCursor(cursor)
                    return

        #auto close quotes etc
        if text in pairs:
            super().keyPressEvent(event)
            self.insertPlainText(pairs[text])
            self.moveCursor(QTextCursor.MoveOperation.Left)
            return

        super().keyPressEvent(event)
        
        if self.completer:
            if text and (text.isalnum() or text == "_"):
                self.handleCompleterUpdate()
            elif not text:
                pass