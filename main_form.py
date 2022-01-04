import sys
import random
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QFileDialog, QStyle, QMessageBox
from PySide6.QtCore import QEvent, Qt

import csv_editor
from csv_editor import CsvEditor, ChangedType
from config import Config


class MainForm(QtWidgets.QMainWindow):
    __csv_file_changed = False      # csv文件是否改变
    __focus_in = True

    def __init__(self):
        super().__init__()

        self.__setup_ui()
        self.__set_title()

        # 定时器更新配置到文件
        self.config_timer = QtCore.QTimer()
        self.config_timer.setInterval(10000)  # 10s
        self.config_timer.timeout.connect(self.write_config_timer)
        self.config_timer.start()

        self.setFocusPolicy(Qt.StrongFocus)

    def __setup_ui(self):
        self.__create_menus()
        self.__create_central()

    def __create_central(self):
        # 主界面
        self.central_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.csv_editor = CsvEditor()
        self.layout.addSpacing(5)
        self.layout.addWidget(self.csv_editor)
        self.setCentralWidget(self.central_widget)
        self.csv_editor.dataChanged.connect(self.csv_changed)

    def __create_menus(self):
        """
        菜单
        :return:
        """
        _file_menu_list = [
            # icon, text, callback, shortcut
            [Config.icon_open_file, '&Open', self.open_csv_file, QtGui.QKeySequence("Ctrl+O")],
            [Config.icon_close_file, '&Close', self.close_csv_file, QtGui.QKeySequence("Ctrl+C")],
            [Config.icon_save_file, '&Save', self.save_csv_file, QtGui.QKeySequence("Ctrl+S")],
            [Config.icon_save_as_file, 'Save As ...', self.save_as_csv_file, QtGui.QKeySequence("")],
        ]
        self.file_menu = self.menuBar().addMenu('&File')
        for icon, txt, func, shortcut in _file_menu_list:
            action = self.file_menu.addAction(txt, func, shortcut)
            action.setIcon(icon)

    def __set_title(self, csv_file=None, modified=False):
        _file = csv_file
        # 如果没有文件，则只显示程序名
        if not _file:
            self.setWindowTitle(Config.app_name)
            return
        # 如果文件改变，则标题头部加*
        if modified:
            _file = "*%s" % _file
        self.setWindowTitle("%s - %s" % (_file, Config.app_name))

    @QtCore.Slot()
    def open_csv_file(self):
        file_name_list = QFileDialog.getOpenFileName(self, '打开文件', Config.open_path, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.load_file(file_name_list[0], with_header=True)
            self.__set_title(file_name_list[0])
            Config.open_path = QtCore.QFileInfo(file_name_list[0]).path()

    @QtCore.Slot()
    def close_csv_file(self):
        self.csv_editor.close_file()
        self.__set_title()

    @QtCore.Slot()
    def save_csv_file(self):
        self.csv_editor.save_file()
        self.__set_title(self.csv_editor.file, False)

    @QtCore.Slot()
    def save_as_csv_file(self):
        file_name_list = QFileDialog.getSaveFileName(self, '保存文件', Config.save_path, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.save_file(file_name_list[0], with_header=True)
            Config.save_path = QtCore.QFileInfo(file_name_list[0]).path()
            self.__set_title(self.csv_editor.file, False)

    @QtCore.Slot()
    def csv_changed(self, type):
        if type == ChangedType.Table:
            self.__set_title(self.csv_editor.file, True)
        else:
            # 窗口在激活状态，则提示重新加载，否则只记录状态
            if self.__focus_in and not self.__csv_file_changed:
                btn = QMessageBox.warning(self, '重新加载', '源文件内容改变，是否重新打开文件？', QMessageBox.Ok | QMessageBox.No)
                if btn == QMessageBox.Ok:
                    self.csv_editor.load_file(self.csv_editor.file, with_header=True)
            else:
                self.__csv_file_changed = True

    def changeEvent(self, event):
        _type = event.type()
        _state = self.windowState()

        # 处理进入、退出最大化事件
        if _type == QEvent.WindowStateChange:
            _maximized = 1 if _state == Qt.WindowMaximized else 0
            if Config.maximized != _maximized:
                Config.maximized = _maximized
                Config.write_config()

    def resizeEvent(self, event):
        _size = event.size()
        Config.size[0] = _size.width()
        Config.size[1] = _size.height()

    def moveEvent(self, event):
        _pos = event.pos()
        Config.position[0] = _pos.x()
        Config.position[1] = _pos.y()

    def closeEvent(self, event):
        Config.write_config()

    def focusInEvent(self, event) -> None:
        self.__focus_in = True
        if self.__csv_file_changed:
            self.__csv_file_changed = False
            btn = QMessageBox.warning(self, '重新加载', '源文件内容改变，是否重新打开文件？', QMessageBox.Ok | QMessageBox.No)
            if btn == QMessageBox.Ok:
                self.csv_editor.load_file(self.csv_editor.file, with_header=True)

    def focusOutEvent(self, event) -> None:
        self.__focus_in = False

    def write_config_timer(self) -> None:
        Config.write_config()
