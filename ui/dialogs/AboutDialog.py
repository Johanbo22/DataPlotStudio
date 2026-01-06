from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

class AboutDialog:
    @staticmethod
    def show_about_dialog(parent, application_version: str):
        """Shows the about dialog"""

        link_to_github_repository = "https://github.com/Johanbo22/DataPlotStudio"
        link_to_data_plot_studio_website = "https://www.data-plot-studio.com"
        message = QMessageBox(parent)
        message.setWindowTitle("About DataPlot Studio")
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        message.setText(
            f"""
            <b>DataPlotStudio v{application_version}</b><br><br>
            A data analysis and visualization tool built with Python and the PyQt6 Framework. <br><br>
            <u>Features:</u><br>
            • Import data from CSV, Excel, JSON, Google Sheets and database connections<br>
            • Tranform and explore your data<br>
            • Create 31 types of visualizations<br>
            • Write custom python code in the integrated python editor to create custom plots<br>
            • Export data after data manipulation<br>
            • Export code for sharing and further customization<br><br>
            <a href="{link_to_github_repository}">Link to Github Repository</a>
            <a href="{link_to_data_plot_studio_website}">Link to website</a>
        """)
        message.exec()