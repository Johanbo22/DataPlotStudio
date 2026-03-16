# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale

from ui.DataPlotStudioApp import DataPlotStudio
from core.tempfilehandling.cleanup_temp_files import cleanup_forgotten_temp_files


def main():
    cleanup_forgotten_temp_files()
    app = QApplication(sys.argv)
    translator = QTranslator()

    if translator.load(QLocale.system(), "dataplotstudio", "_", "translations"):
        app.installTranslator(translator)

    window = DataPlotStudio()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
