import sys
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QFileDialog, QStyle, QMessageBox
from PySide6.QtCore import QEvent, Qt, QFileInfo
from csv_editor import CsvEditor
from config import Config
from qt_material import list_themes
from qt_material import apply_stylesheet


class MainForm(QtWidgets.QMainWindow):
    __csvChanged = False      # csv文件是否改变
    __tableChanged = False    # 表格数据是否改变
    __focusIn = True
    __withHeader = True

    def __init__(self):
        super().__init__()

        self.__setupUi()
        self.__setTitle()

        # 定时器更新配置到文件
        self.config_timer = QtCore.QTimer()
        self.config_timer.setInterval(10000)  # 10s
        self.config_timer.timeout.connect(self.writeConfigTimer)
        self.config_timer.start()

        self.setFocusPolicy(Qt.StrongFocus)

        # 如果有入参，则打开入参指定的文件
        if len(sys.argv) > 1 and QFileInfo(sys.argv[1]).isFile():
            self.csv_editor.loadFile(sys.argv[1], withHeader=self.__withHeader)
            self.__setTitle(sys.argv[1])
            Config.openPath = QFileInfo(sys.argv[1]).path()

    def __setupUi(self):
        self.__createMenuAndToolBar()
        self.__createCentral()

    def __createCentral(self):
        # 主界面
        self.central_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.csv_editor = CsvEditor()
        self.layout.addSpacing(5)
        self.layout.addWidget(self.csv_editor)
        self.setCentralWidget(self.central_widget)

        # 信号槽
        self.csv_editor.dataChanged.connect(self.changed)
        self.csv_editor.fileDroped.connect(self.fileDroped)

    def __createMenuAndToolBar(self):
        """
        菜单栏和工具栏
        :return:
        """
        # >> 文件菜单
        _fileMenuList = [
            # icon, text, callback, shortcut
            [Config.iconOpenFile, '&Open', self.openFile, QtGui.QKeySequence("Ctrl+O")],
            [Config.iconCloseFile, '&Close', self.closeFile, QtGui.QKeySequence("Ctrl+C")],
            [Config.iconSaveFile, '&Save', self.saveFile, QtGui.QKeySequence("Ctrl+S")],
            [Config.iconSaveAsFile, 'Save As ...', self.saveAsFile, QtGui.QKeySequence("")],
        ]
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileToolBar = self.addToolBar('&File')
        for icon, txt, func, shortcut in _fileMenuList:
            action = self.fileMenu.addAction(txt, func, shortcut)
            action.setIcon(icon)
            self.fileToolBar.addAction(action)

        # >> 显示菜单
        self.viewMenu = self.menuBar().addMenu('&View')
        # 主题
        self.themeActionGroup = QtGui.QActionGroup(self)
        self.themeActionGroup.setExclusionPolicy(QtGui.QActionGroup.ExclusionPolicy.Exclusive)
        self.themeMenu = self.viewMenu.addMenu('&Theme')
        _themeList = list_themes()
        _themeList.insert(0, 'None.xml')
        for theme in _themeList:
            _action = self.themeMenu.addAction(theme[:-4], self.setTheme)
            _action.setCheckable(True)
            self.themeActionGroup.addAction(_action)
            if theme[:-4] == Config.theme:
                _action.setChecked(True)

    def __setTitle(self, csv_file=None, modified=False):
        _file = csv_file
        # 如果没有文件，则只显示程序名
        if not _file:
            self.setWindowTitle(Config.appName)
            return
        # 如果文件改变，则标题头部加*
        if modified:
            _file = "*%s" % _file
        self.setWindowTitle("%s - %s" % (_file, Config.appName))

    @QtCore.Slot()
    def openFile(self):
        # 判断当前是否有文件打开
        if self.csv_editor.opened:
            btn = QMessageBox.warning(self, '打开文件', '是否关闭当前文件？', QMessageBox.Ok | QMessageBox.No)
            if btn == QMessageBox.Ok:
                self.closeFile()
            else:
                return

        # 打开文件
        file_name_list = QFileDialog.getOpenFileName(self, '打开文件', Config.openPath, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.loadFile(file_name_list[0], withHeader=self.__withHeader)
            self.__setTitle(file_name_list[0])
            Config.openPath = QtCore.QFileInfo(file_name_list[0]).path()

    @QtCore.Slot()
    def closeFile(self):
        if self.__tableChanged:
            btn = QMessageBox.warning(self, '保存', '表格内容发生修改，是否保存文件？', QMessageBox.Ok | QMessageBox.No)
            if btn == QMessageBox.Ok:
                self.csv_editor.saveFile(self.csv_editor.file, withHeader=self.__withHeader)
        self.csv_editor.closeFile()
        self.__setTitle()
        self.__tableChanged = False

    @QtCore.Slot()
    def saveFile(self):
        self.csv_editor.saveFile(withHeader=True)
        self.__setTitle(self.csv_editor.file, False)
        self.__tableChanged = False
        QMessageBox.information(self, '保存', '保存成功')

    @QtCore.Slot()
    def saveAsFile(self):
        file_name_list = QFileDialog.getSaveFileName(self, '保存文件', Config.savePath, filter='CSV File (*.csv)')
        if file_name_list and len(file_name_list) > 0 and len(file_name_list[0]) > 0:
            self.csv_editor.saveFile(file_name_list[0], withHeader=True)
            Config.savePath = QtCore.QFileInfo(file_name_list[0]).path()
            self.__setTitle(self.csv_editor.file, False)
            self.__tableChanged = False
            QMessageBox.information(self, '另保存', '保存成功')

    @QtCore.Slot()
    def changed(self, type):
        """
        1. 表格内容改变
        2. 源文件内容改变
        :param type:
        :return:
        """
        if type == CsvEditor.ChangedType.Table:
            self.__tableChanged = True
            self.__setTitle(self.csv_editor.file, True)
        else:
            # 窗口在激活状态，则提示重新加载，否则只记录状态
            if self.__focusIn and not self.__csvChanged:
                btn = QMessageBox.warning(self, '重新加载', '源文件内容改变，是否重新打开文件？', QMessageBox.Ok | QMessageBox.No)
                if btn == QMessageBox.Ok:
                    self.csv_editor.loadFile(self.csv_editor.file, withHeader=True)
            else:
                self.__csvChanged = True

    @QtCore.Slot()
    def setTheme(self):
        _theme = self.sender().text()
        Config.theme = _theme
        if _theme == 'None':
            QtWidgets.QApplication.instance().setStyleSheet("")
        else:
            apply_stylesheet(QtWidgets.QApplication.instance(), _theme + '.xml')

    @QtCore.Slot()
    def fileDroped(self, file: str):
        # 判断当前是否有文件打开.若打开的文件相同，则不处理
        if self.csv_editor.opened:
            if self.csv_editor.file == file:
                return
            btn = QMessageBox.warning(self, '打开文件', '是否关闭当前文件？', QMessageBox.Ok | QMessageBox.No)
            if btn == QMessageBox.Ok:
                self.closeFile()
            else:
                return

        # 打开文件
        self.csv_editor.loadFile(file, withHeader=self.__withHeader)
        self.__setTitle(file)
        Config.openPath = QtCore.QFileInfo(file).path()

    def changeEvent(self, event):
        _type = event.type()
        _state = self.windowState()

        # 处理进入、退出最大化事件
        if _type == QEvent.WindowStateChange:
            _maximized = 1 if _state == Qt.WindowMaximized else 0
            if Config.maximized != _maximized:
                Config.maximized = _maximized
                Config.writeConfig()

    def resizeEvent(self, event):
        _size = event.size()
        Config.size[0] = _size.width()
        Config.size[1] = _size.height()

    def moveEvent(self, event):
        _pos = event.pos()
        Config.position[0] = _pos.x()
        Config.position[1] = _pos.y()

    def closeEvent(self, event):
        Config.writeConfig()

    def focusInEvent(self, event) -> None:
        self.__focusIn = True
        if self.__csvChanged:
            self.__csvChanged = False
            btn = QMessageBox.warning(self, '重新加载', '源文件内容改变，是否重新打开文件？', QMessageBox.Ok | QMessageBox.No)
            if btn == QMessageBox.Ok:
                self.csv_editor.loadFile(self.csv_editor.file, withHeader=True)

    def focusOutEvent(self, event) -> None:
        self.__focusIn = False

    def writeConfigTimer(self) -> None:
        Config.writeConfig()
