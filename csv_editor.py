import csv
import enum
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Slot, Signal, QFileSystemWatcher, Qt, QFileInfo
from PySide6.QtGui import QPalette, QDragEnterEvent, QDropEvent


class CsvEditor(QWidget):
    """
    csv编辑器控件
    """

    class ChangedType(enum.Enum):
        """
        改变类型：表格内容改变/源文件改变
        """
        Table = 0  # 表格内容改变
        File = 1   # csv文件改变

    # 信号
    dataChanged = Signal(ChangedType)       # 数据改变的信号:表格&文件
    fileDroped = Signal(str)                # 文件拖放的信号

    # 私有类变量
    __tableChanged = False                  # 记录表格内容是否改变
    __file = None                           # 保存当前打开的文件
    __fileWatcher = QFileSystemWatcher()    # 文件监视器

    def __init__(self):
        super().__init__()
        self.__setupUi()

    def __setupUi(self):
        self.table = QTableWidget()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table)
        self.table.setAlternatingRowColors(True)
        self.table.setPalette(QPalette(Qt.lightGray))
        self.table.setVisible(False)

        self.__fileWatcher.fileChanged.connect(self.fileChanged)
        self.setAcceptDrops(True)

    def __setHeader(self, header):
        """
        设置表头
        :param header: 列表
        :return: None
        """
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)

    def __appendRow(self, row):
        """
        添加一行数据
        :param row: 列表
        :return: None
        """
        # 如果当前行的列数超过了之前的列数，则重新设置列数
        item_count = len(row)
        column_count = self.table.columnCount()
        if item_count > column_count:
            self.table.setColumnCount(item_count)

        # 插入新行
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for i, item in enumerate(row):
            self.table.setItem(row_count, i, QTableWidgetItem(item))

    @Slot()
    def fileChanged(self, file):
        """
        源文件改变
        :param file:
        :return:
        """
        if file == self.__file:
            self.dataChanged.emit(CsvEditor.ChangedType.File)

    @Slot()
    def tableChanged(self):
        """
        表格内容改变
        :return:
        """
        self.__tableChanged = True
        self.dataChanged.emit(CsvEditor.ChangedType.Table)

    @property
    def file(self):
        """
        获取当前的文件
        :return:
        """
        return self.__file

    @property
    def opened(self) -> bool:
        """
        是否有文件打开
        :return:
        """
        if self.__file:
            return True
        else:
            return False

    def loadFile(self, csvFile, withHeader=False):
        """
        加载csv文件
        :param csvFile: csv文件路径
        :param withHeader: 是否有列头
        :return: None
        """
        # 清楚表格
        self.closeFile()

        # 读文件，并填充表格
        with open(csvFile, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_index = 0
            for row in reader:
                if withHeader and row_index == 0:
                    # 设置header
                    self.__setHeader(row)
                else:
                    # 添加一行
                    self.__appendRow(row)
                row_index += 1

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.Stretch)

        # 记录状态
        # 1. 清除表格内容改变的状态
        # 2. 保存当前文件
        # 3. 显示该控件
        # 4. 连接信号槽
        # 5. 监视该文件
        self.__tableChanged = False
        self.__file = csvFile
        self.table.setVisible(True)
        self.table.itemChanged.connect(self.tableChanged)
        self.__fileWatcher.addPath(csvFile)

    def closeFile(self):
        """
        关闭
        :return:
        """
        # 清除状态
        # 1. 移除监视该文件
        # 2. 断开信号槽
        # 3. 隐藏该控件
        # 4. 清除当前文件
        # 5. 清空表格
        # 6. 清除记录表格内容改变的状态位
        if self.__file:
            self.__fileWatcher.removePath(self.__file)
            self.table.itemChanged.disconnect(self.tableChanged)
            self.table.setVisible(False)
            self.__file = None
            self.table.clear()
            self.table.setColumnCount(0)
            self.table.setRowCount(0)
            self.__tableChanged = False

    def saveFile(self, csvFile=None, withHeader=False):
        """
        保存文件
        :param csvFile: 保存到的文件名。None: 保存到当前文件
        :param withHeader: 是否保存列头
        :return:
        """
        # csvFile为空，则使用当前文件
        if not csvFile:
            csvFile = self.__file
        if not csvFile:
            return

        # 将表格数据写入到文件
        with open(csvFile, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            row_count = self.table.rowCount()
            column_count = self.table.columnCount()

            # 写header
            if withHeader:
                header = []
                for i in range(0, column_count):
                    item = self.table.horizontalHeaderItem(i).text()
                    header.append(item)
                writer.writerow(header)

            rows = []
            for row_idx in range(0, row_count):
                # 获取当前行的数据
                row = []
                for column_idx in range(0, column_count):
                    item = self.table.item(row_idx, column_idx).text()
                    row.append(item)
                rows.append(row)

                # 防止内存开销过大，因此指定行数写入一次
                if len(rows) == 1000:
                    writer.writerows(rows)
                    rows = []

            # 写入剩余数据
            if len(rows):
                writer.writerows(rows)

        # 另存为时，更新状态
        # 1. 清除表格内容改变的标志位
        # 2. 移除监视的旧文件
        # 3. 监视新文件
        # 4. 更新当前文件
        self.__tableChanged = False
        if self.__file != csvFile:
            self.__fileWatcher.removePath(self.__file)
            self.__fileWatcher.addPath(csvFile)
            self.__file = csvFile

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            _urls = event.mimeData().urls()
            # 1. 没有文件或者文件数量大于1，都不处理
            # 2. 是文件夹，也不处理
            if (not _urls) or (len(_urls) > 1):
                event.ignore()
                return
            elif QFileInfo(_urls[0].toLocalFile()).isDir():
                event.ignore()
                return
            # 接受drop事件
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            _file = event.mimeData().urls()[0].toLocalFile()
            self.fileDroped.emit(_file)
        else:
            event.ignore()
