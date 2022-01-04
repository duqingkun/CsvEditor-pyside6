import csv
import enum
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Slot, Signal, QFileSystemWatcher


class Status(enum.Enum):
    Opened = 0
    Closed = 1


class ChangedType(enum.Enum):
    Table = 0  # 表格内容改变
    File = 1   # csv文件改变


class CsvEditor(QWidget):
    # 公共类变量
    status = Status.Closed
    dataChanged = Signal(ChangedType)

    # 私有类变量
    __changed = False
    __file = None
    __fileWatcher = QFileSystemWatcher()

    def __init__(self):
        super().__init__()
        self.__setup_ui()

    def __setup_ui(self):
        self.table = QTableWidget()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table)
        self.setVisible(False)

        self.__fileWatcher.fileChanged.connect(self.file_changed)

    def __set_header(self, header):
        """
        设置表头
        :param header: 列表
        :return: None
        """
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)

    def __append_row(self, row):
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
    def file_changed(self, file):
        if file == self.__file:
            self.dataChanged.emit(ChangedType.File)

    @Slot()
    def csv_changed(self):
        self.dataChanged.emit(ChangedType.Table)

    @property
    def file(self):
        return self.__file

    def load_file(self, csv_file, with_header=False):
        """
        加载csv文件
        :param csv_file: csv文件路径
        :param with_header: 是否有列头
        :return: None
        """
        # 清楚表格
        self.close_file()

        # 读文件，并填充表格
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_index = 0
            for row in reader:
                if with_header and row_index == 0:
                    # 设置header
                    self.__set_header(row)
                else:
                    # 添加一行
                    self.__append_row(row)
                row_index += 1
        self.status = Status.Opened
        self.__file = csv_file
        self.setVisible(True)
        self.table.itemChanged.connect(self.csv_changed)
        self.__fileWatcher.addPath(csv_file)

    def close_file(self):
        """
        关闭
        :return:
        """
        if self.__file:
            self.__fileWatcher.removePath(self.__file)
            self.table.itemChanged.disconnect(self.csv_changed)
        self.table.clear()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.status = Status.Closed
        self.__file = None
        self.setVisible(False)

    def save_file(self, csv_file=None, with_header=False):
        if not csv_file:
            csv_file = self.__file
        if not csv_file:
            return

        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            row_count = self.table.rowCount()
            column_count = self.table.columnCount()

            # 写header
            if with_header:
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
