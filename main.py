# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale

from ui.DataPlotStudioApp import DataPlotStudio


def main():
    print("DEBUG: Application starting")
    app = QApplication(sys.argv)
    translator = QTranslator()

    if translator.load(QLocale.system(), "dataplotstudio", "_", "translations"):
        app.installTranslator(translator)

    qss = DataPlotStudio.load_stylesheet("styles/style.css")
    app.setStyleSheet(qss)
    
    window = DataPlotStudio()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()