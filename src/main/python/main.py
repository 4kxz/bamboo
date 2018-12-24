import sys

from fbs_runtime.application_context import ApplicationContext
from IPython.terminal.embed import InteractiveShellEmbed
from pandas import DataFrame
from pandas import read_csv
from pandas import set_option
from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QVBoxLayout


class AppContext(ApplicationContext):
    def run(self):
        window = AppMainWindow()
        window.showMaximized()
        return self.app.exec_()


class PandasTableView(QTableView):
    pass


class PandasDataframeModel(QAbstractTableModel):
    def __init__(self, *args, dataframe, **kwargs):
        super().__init__(*args, **kwargs)
        self._dataframe: DataFrame = dataframe
        by = self._dataframe.columns[0]
        self._dataframe.sort_values(by=by, ascending=True, inplace=True)

    def rowCount(self, parent=None):
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        return self._dataframe.shape[1]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole and index.isValid():
            return str(self._dataframe.iloc[index.row(), index.column()])
        else:
            return QVariant()

    def sort(self, column, order):
        by = self._dataframe.columns[column]
        ascending = order == QtCore.Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._dataframe.sort_values(by=by, ascending=ascending, inplace=True)
        self.layoutChanged.emit()

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
        self._load("~/Documents/sample.csv")

    def _init_ui(self):
        self.setWindowTitle(f"Bamboos")
        self.resize(1280, 720)
        self._init_menu()
        self._init_table()

    def _init_table(self):
        self._table = PandasTableView()
        self._table.setSortingEnabled(True)
        self.setCentralWidget(self._table)

    def _init_menu(self):
        menu_bar: QMenuBar = self.menuBar()
        f: QMenu = menu_bar.addMenu("&File")
        f.addAction(self._action("&Open", "Ctrl+O", self._open))
        f.addAction(self._action("&Console", "Ctrl+T", self._console))
        d: QMenu = menu_bar.addMenu("&DataFrame")
        d.addAction(self._action("&Describe", "Ctrl+Shift+D", self._describe))

    def _load(self, file_name):
        self.setWindowTitle(f"{file_name} - Bamboos")
        self._dataframe = read_csv(file_name)
        model = PandasDataframeModel(dataframe=self._dataframe)
        self._table.setModel(model)
        self._table.resizeColumnsToContents()
        self._status()

    def _status(self):
        n, m = self._dataframe.shape
        self.statusBar().addWidget(QLabel(f"{n} rows, {m} columns"))

    def _open(self):
        file_name, _ = QFileDialog.getOpenFileName()
        if not file_name:
            return
        self._load(file_name)

    def _describe(self):
        dataframe = self._dataframe.describe()
        model = PandasDataframeModel(dataframe=dataframe)
        table = PandasTableView(self)
        table.setModel(model)
        table.resizeColumnsToContents()
        dialog = QDialog(self)
        dialog.resize(self.size() * 0.9)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        layout.addWidget(table)
        dialog.exec_()

    def _console(self):
        df = self._dataframe  # noqa
        shell()

    def _action(self, label, shortcut, callback):
        action = QAction(QIcon("icon.ico"), label, self)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action


if __name__ == "__main__":
    shell = InteractiveShellEmbed()
    shell.enable_gui("qt5")
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
    set_option("precision", 1)
