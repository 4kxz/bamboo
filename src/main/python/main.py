import sys

from fbs_runtime.application_context import ApplicationContext
from IPython.terminal.embed import InteractiveShellEmbed
from pandas import DataFrame
from pandas import read_csv
from pandas import Series
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
    def __init__(self, dataframe, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data: DataFrame = dataframe
        by = self.__data.columns[0]
        self.__data.sort_values(by=by, ascending=True, inplace=True)

    def rowCount(self, parent=None):
        return self.__data.shape[0]

    def columnCount(self, parent=None):
        return self.__data.shape[1]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole and index.isValid():
            return str(self.__data.iloc[index.row(), index.column()])
        else:
            return QVariant()

    def sort(self, column, order):
        by = self.__data.columns[column]
        ascending = order == QtCore.Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self.__data.sort_values(by=by, ascending=ascending, inplace=True)
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.__data.columns[section])
            else:
                return str(self.__data.index[section])
        else:
            return QVariant()


class PandasSeriesModel(QAbstractTableModel):
    def __init__(self, series, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data: Series = series

    def rowCount(self, parent=None):
        return self.__data.shape[0]

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole and index.isValid():
            return str(self.__data.iloc[index.row()])
        else:
            return QVariant()

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return "Values"
            else:
                return str(self.__data.index[section])
        else:
            return QVariant()


class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui()
        self.__load("~/Documents/sample.csv")

    def __init_ui(self):
        self.setWindowTitle(f"Bamboos")
        self.resize(1280, 720)
        self.__init_table()
        self.__init_menu()

    def __init_table(self):
        self.__table_view = PandasTableView()
        self.__table_view.setSortingEnabled(True)
        self.setCentralWidget(self.__table_view)

    def __init_menu(self):
        menu_bar: QMenuBar = self.menuBar()
        f: QMenu = menu_bar.addMenu("&File")
        f.addAction(self.__action("&Open", "Ctrl+O", self.__open))
        f.addAction(self.__action("&Console", "Ctrl+T", self.__console))
        d: QMenu = menu_bar.addMenu("&Data")
        d.addAction(self.__action("&Describe", "Ctrl+Shift+D", self.__describe))
        d.addAction(self.__action("&Count", "Ctrl+Shift+C", self.__count))

    def __load(self, file_name):
        self.setWindowTitle(f"{file_name} - Bamboos")
        self.__dataframe = read_csv(file_name)
        self.__table_view.setModel(PandasDataframeModel(self.__dataframe))
        self.__table_view.resizeColumnsToContents()
        self.__status()

    def __status(self):
        n, m = self.__dataframe.shape
        self.statusBar().addWidget(QLabel(f"{n} rows, {m} columns"))

    def __open(self):
        file_name, _ = QFileDialog.getOpenFileName()
        if not file_name:
            return
        self.__load(file_name)

    def __describe(self):
        data = self.__dataframe.describe()
        self.__show_table(data, title="Describe")

    def __count(self):
        data = self.__dataframe.count()
        self.__show_table(data, title="Count")

    def __show_table(self, data, title=""):
        table = PandasTableView(self)
        table.setModel(self.__get_table_model(data))
        table.resizeColumnsToContents()
        dialog = QDialog(self)
        dialog.resize(self.size() * 0.9)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        layout.addWidget(table)
        dialog.setWindowTitle(title)
        dialog.exec_()

    def __get_table_model(self, data):
        if isinstance(data, DataFrame):
            return PandasDataframeModel(data)
        elif isinstance(data, Series):
            return PandasSeriesModel(data)

    def __console(self):
        df = self.__dataframe  # noqa
        shell()

    def __action(self, label, shortcut, callback):
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
