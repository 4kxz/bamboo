import sys

from fbs_runtime.application_context import ApplicationContext
from pandas import read_csv
from pandas import DataFrame
from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QTableView


class AppContext(ApplicationContext):
    def run(self):
        window = AppMainWindow()
        window.showMaximized()
        return self.app.exec_()


class PandasTableView(QTableView):
    pass


class PandasTableModel(QAbstractTableModel):

    def __init__(self, *args, file_name, **kwargs):
        super().__init__(*args, **kwargs)
        self._dataframe: DataFrame = read_csv(file_name, index_col=0)

    def rowCount(self, parent=None):
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        return self._dataframe.shape[1]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole and index.isValid():
            return str(self._dataframe.iloc[index.row(), index.column()])
        else:
            return QVariant()

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._dataframe.columns[section])
            else:
                return str(self._dataframe.index[section])
        else:
            return QVariant()


class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load("/home/carlos/Documents/sample.csv")

    def _init_ui(self):
        self.setWindowTitle(f"Bamboos")
        self.resize(1280, 720)
        self._init_menu()
        self._init_table()

    def _init_table(self):
        self._table = PandasTableView()
        self.setCentralWidget(self._table)

    def _init_menu(self):
        menu_bar: QMenuBar = self.menuBar()
        file_menu: QMenu = menu_bar.addMenu("&File")
        open_action = QAction(QIcon("icon.ico"), "&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open)
        file_menu.addAction(open_action)
        menu_bar.addMenu("&About")

    def _open(self):
        file_name, _ = QFileDialog.getOpenFileName()
        if not file_name:
            return
        self._load(file_name)

    def _load(self, file_name):
        self.setWindowTitle(f"Bamboos - {file_name}")
        model = PandasTableModel(file_name=file_name)
        self._table.setModel(model)


if __name__ == "__main__":
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
