import sys
import random
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QFileDialog, QStyle
from PySide6.QtCore import QEvent
from csv_editor import CsvEditor
from config import Config


class MainForm(QtWidgets.QMainWindow):
    __title_bar_height = 0  # 标题栏高度

    def __init__(self):
        super().__init__()

        self.__setup_ui()
        self.__set_title(Config.app_name)

        # 定时器更新配置到文件
        self.config_timer = QtCore.QTimer()
        self.config_timer.setInterval(10000)  # 10s
        self.config_timer.timeout.connect(self.write_config_timer)
        self.config_timer.start()

        self.__title_bar_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight)

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

    def __set_title(self, title):
        self.setWindowTitle(title)

    @QtCore.Slot()
    def open_csv_file(self):
        file_name_list = QFileDialog.getOpenFileName(self, '打开文件', Config.open_path, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.load_file(file_name_list[0], with_header=True)
            self.__set_title("%s - %s" % (file_name_list[0], Config.app_name))
            Config.open_path = QtCore.QFileInfo(file_name_list[0]).path()

    @QtCore.Slot()
    def close_csv_file(self):
        self.csv_editor.close_file()
        self.__set_title(Config.app_name)

    @QtCore.Slot()
    def save_csv_file(self):
        self.csv_editor.save_file()

    @QtCore.Slot()
    def save_as_csv_file(self):
        file_name_list = QFileDialog.getSaveFileName(self, '保存文件', Config.save_path, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.save_file(file_name_list[0], with_header=True)
            Config.save_path = QtCore.QFileInfo(file_name_list[0]).path()

    def changeEvent(self, event):
        if event.type() != QEvent.WindowStateChange:
            return
        if self.windowState() == QtCore.Qt.WindowMaximized:
            Config.maximized = 1
        else:
            Config.maximized = 0

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

    def write_config_timer(self):
        Config.write_config()
