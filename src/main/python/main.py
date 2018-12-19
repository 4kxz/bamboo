import sys

from fbs_runtime.application_context import ApplicationContext
from pandas import read_csv
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem


class AppContext(ApplicationContext):
    def run(self):
        window = AppMainWindow()
        window.showMaximized()
        return self.app.exec_()


class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data("/home/carlos/Documents/sample.csv")

    def _init_ui(self):
        self._init_menu()
        self._table = QTableWidget()
        self.setCentralWidget(self._table)
        self.resize(1280, 720)
        self.setWindowTitle(f"Bamboos")

    def _init_menu(self):
        menu_bar: QMenuBar = self.menuBar()
        file_menu: QMenu = menu_bar.addMenu("&File")
        open_action = QAction(QIcon("icon.ico"), "&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open)
        file_menu.addAction(open_action)

    def _open(self):
        file_name, _ = QFileDialog.getOpenFileName()
        self._load_data(file_name)

    def _load_data(self, file_name):
        if not file_name:
            return
        self.setWindowTitle(f"Bamboos - {file_name}")
        df = read_csv(file_name).head()
        n, m = df.shape
        self._table.setRowCount(n)
        self._table.setColumnCount(m)
        self._table.setHorizontalHeaderLabels(df.columns)
        for i in range(n):
            for j in range(m):
                value = str(df.iloc[i, j])
                item = QTableWidgetItem(value)
                self._table.setItem(i, j, item)


if __name__ == "__main__":
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
