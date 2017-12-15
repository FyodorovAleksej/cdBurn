import re
import sys

def ACTIVE():
    return QColor(125,225,125)

def DEACTIVE():
    return QColor(225, 125, 125)
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QTreeWidgetItem, QListWidgetItem, QSystemTrayIcon, \
    QStyle, QAction, qApp, QMenu

from cdAdapter import CDAdapter
from mainwindow import Ui_MainWindow


# Main Window class
class MyWin(QtWidgets.QMainWindow):
    # wifi Adapter for working with wifi connections
    cdAdapter = CDAdapter()
    tray_icon = None

    # construct window
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # default column size
        self.ui.filesTable.setColumnCount(2)
        self.ui.filesTable.insertRow(self.ui.filesTable.rowCount())
        # initialize headers of table
        header1 = QTableWidgetItem("path")
        header2 = QTableWidgetItem("name")
        # set headers
        self.ui.filesTable.setHorizontalHeaderItem(0, header1)
        self.ui.filesTable.setHorizontalHeaderItem(1, header2)
        # settings for table items
        self.ui.filesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        headers = self.ui.filesTable.horizontalHeader()
        headers.setStretchLastSection(True)
        # set 0 rows as default
        self.ui.filesTable.setRowCount(0)
        # connecting buttons
        self.ui.addButton.clicked.connect(self.add)
        self.ui.deleteButton.clicked.connect(self.delete)
        self.ui.writeButton.clicked.connect(self.write)
        self.ui.filesTable.doubleClicked.connect(self.doubleClick)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.getcwd() + "/tray.png"))
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # close action
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "cdBurn",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )

    # append strings in table in columns
    def appendText(self, file):
        local = re.findall(r"([a-zA-Z-_0-9]+)\.", str(file).strip('\n'))
        extension = re.findall(r"\.([a-zA-Z-_0-9]+)", str(file).strip('\n'))
        if (extension == []):
            local = local[0]
        else:
            local = local[0] + "."+ extension[0]
        item1 = QTableWidgetItem(str(file))
        item1.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        item2 = QTableWidgetItem(local)
        item2.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        # validate last item
        table = self.ui.filesTable
        curitem = table.item(table.rowCount() - 1, 0)
        if (curitem != None):
            # adding new row in table
            table.insertRow(table.rowCount())
        # if table is empty
        if (table.rowCount() == 0):
            table.setRowCount(1)
        item1.setBackground(ACTIVE())
        item2.setBackground(ACTIVE())
        table.setItem(table.rowCount() - 1, 0, item1)
        table.setItem(table.rowCount() - 1, 1, item2)

    def doubleClick(self, index):
        item1 = self.ui.filesTable.item(index.row(), 0)
        item2 = self.ui.filesTable.item(index.row(), 1)
        if (item1.background() == ACTIVE()):
            item1.setBackground(DEACTIVE())
            item2.setBackground(DEACTIVE())
            self.logging("Total size: "+ str(self.totalSize()) + " bytes")
            return

        if (item1.background() == DEACTIVE()):
            item1.setBackground(ACTIVE())
            item2.setBackground(ACTIVE())
            self.logging("Total size: "+ str(self.totalSize()) + " bytes")
            return


    def delItems(self, indexes):
        for index in indexes:
            item1 = self.ui.filesTable.item(index.row(), 0)
            item2 = self.ui.filesTable.item(index.row(), 1)
            del item1
            del item2
            self.ui.filesTable.removeRow(index.row())

    def delete(self):
        indexes = self.ui.filesTable.selectionModel().selectedRows()
        self.delItems(sorted(indexes, reverse=True))
        self.logging("Total size: "+ str(self.totalSize()) + " bytes")

    def add(self):
        file = QtWidgets.QFileDialog.getOpenFileUrl(parent = self, caption = "Выберите файл", filter = "Все файлы (*)")[0].toLocalFile()
        print(file)
        self.appendText(file)
        self.logging("Total size: "+ str(self.totalSize()) + " bytes")


    def write(self):
        names = []
        for i in range(0, self.ui.filesTable.rowCount()):
            if (self.ui.filesTable.item(i, 0).background() == ACTIVE()):
                name = {"path" : self.ui.filesTable.item(i, 0).text(), "name" : self.ui.filesTable.item(i, 1).text()}
                names.append(name)
        self.logging(self.cdAdapter.write(names))
        self.cdAdapter.burnProcess.readyRead.connect(self.writeLogging)

    def writeLogging(self):

        readline = str(self.cdAdapter.burnProcess.readAllStandardOutput()).split("\'")[1]
        print(readline)
        if ("Writing:" in readline):
            readline = readline.split("fifo")[0]
            readline = readline.split("Writing:")[1]
            readline = readline.split("s")[1]
            readline = readline.split(".")[0]
            self.ui.writeProgressBar.setValue(int(readline))
        if ("completed successfully" in readline):
            self.logging("Writing Succesfully")
            self.ui.writeProgressBar.setValue(0)
        if ("Written to" in readline):
            self.logging("Writing Succesfully")
            self.ui.writeProgressBar.setValue(0)


    def totalSize(self):
        sum = 0
        for i in range(0, self.ui.filesTable.rowCount()):
            if (self.ui.filesTable.item(i, 0).background() == QColor(125, 225, 125)):
                sum += os.path.getsize(self.ui.filesTable.item(i, 0).text())
        return sum

    # print info about connecting
    def logging(self, message):
        print(message)
        if (message != None):
            self.ui.infoLabel.setText("info: " + message)
            self.tray_icon.showMessage(
                "cdBurn",
                message,
                QSystemTrayIcon.Information,
                2000
            )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWin()
    window.show()

    # umount /dev/sr0 & xorriso -outdev /dev/sr0 -blank as_needed map /home/alexey/Music/Bass-Drum-2.wav /files/Bass-Drum-2.wav commit_eject all 2>&1
    # umount /dev/sr0 & xorriso -outdev /dev/sr0 -blank as_needed map /home/alexey/Music/Bass-Drum-2.wav /sound/Bass-Drum-2.wav commit_eject all 2>&1
    sys.exit(app.exec_())
    exit()
