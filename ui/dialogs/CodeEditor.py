from ui.LineNumberArea import LineNumberArea


from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QTextCursor, QTextFormat
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit


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

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        text = event.text()

        pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        closing_chars = {')', ']', '}', '"', "'"}

        #tabs
        if event.key() == Qt.Key.Key_Tab:
            cursor.insertText("    ")
            return

        #backtab (wip)
        if event.key() == Qt.Key.Key_Backtab:
            pass

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