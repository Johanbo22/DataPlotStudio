from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPen

from ui.help_animation_engine import HelpAnimationEngine

class Animation(HelpAnimationEngine):
    """Animation to show duplicate rows being removed"""

    def __init__(self):
        super().__init__(duration_ms=5000)

        # Data Representation
        self.data_rows = [
            {"id": "A", "val": 10, "dup": False},
            {"id": "B", "val": 20, "dup": False},
            {"id": "A", "val": 10, "dup": True},
            {"id": "C", "val": 30, "dup": False},
            {"id": "B", "val": 20, "dup": True},
            {"id": "D", "val": 40, "dup": False}
        ]

        self.row_height = 35
        self.row_width = 300
        self.start_x = (self.width() - self.row_width) / 2
        self.start_y = 40

    def draw_animation(self, painter, progress):

        highlight_progress = self.get_eased_progerss(progress, 0.05, 0.3)
        fade_progress = self.get_eased_progerss(progress, 0.035, 0.6)
        collapse_progress = self.get_eased_progerss(progress, 0.6, 0.8)

        painter.setFont(self.font_main)

        current_y_offset = 0

        #Draw a title
        painter.setPen(self.text_color)
        painter.drawText(QRectF(0, 5, self.width(), 30), Qt.AlignmentFlag.AlignCenter, "Operation: Remove Duplicates")
        removed_count =0

        for i, row in enumerate(self.data_rows):
            
            # base positions
            x = self.start_x
            y = self.start_y + (i * (self.row_height + 5))

            #Opacity
            opacity = 1.0
            if row["dup"]:
                opacity = 1.0 - fade_progress
            
            target_y_shift = 0
            if not row["dup"]:
                dups_above = sum(1 for r in self.data_rows[:i] if r["dup"])
                target_y_shift = dups_above * (self.row_height + 5) * collapse_progress
            
            y -= target_y_shift

            # Draw row
            if opacity > 0:
                painter.setOpacity(opacity)

                # Determine color
                bg_color = QColor("#3d3d3d")
                text_color = self.text_color

                # Highlighting
                if row["dup"] and highlight_progress > 0:
                    #Interpolate
                    r = 61 + (231 - 61) * highlight_progress
                    g = 61 + (76 - 61) * highlight_progress
                    b = 61 + (60 - 61) * highlight_progress
                    bg_color = QColor(int(r), int(g), int(b))
                
                rect = QRectF(x, y, self.row_width, self.row_height)

                # Draw cells
                painter.setBrush(bg_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect, 4, 4)

                # Draw text
                painter.setPen(text_color)
                text_rect = rect.adjusted(10, 0, -10, 0)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"ID: {row['id']}")
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"Value: {row['val']}")

                # Draw duplicate indicator
                if row["dup"] and opacity > 0.5:
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "DUPLICATE")
        
        painter.setOpacity(1.0)