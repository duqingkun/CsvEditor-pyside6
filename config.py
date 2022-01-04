# -*- coding:UTF-8 -*-

"""
@Project : CsvEditor 
@File    : config.py
@Desc    : 全局配置文件
@Author  : qdu
@Date    : 2022/1/4 17:01 
"""

from PySide6.QtCore import QSettings, QMutex
from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtGui import QIcon


class Icon(object):
    open_file = None
    close_file = None
    save_file = None
    save_as_file = None


class Config(object):
    # 可读写配置项
    position = [0, 0]  # 窗体初始位置（左上角x y坐标）
    size = [800, 600]  # 窗体初始大小（width,height）
    maximized = False  # 是否最大化显示
    open_path = '.'
    save_path = '.'

    # 私有属性
    __file = 'config.ini'
    __write_mutex = QMutex()
    __icon = Icon()
    __app_name = 'CSV Editor'

    # 只读配置项
    @classmethod
    @property
    def app_name(cls):
        return cls.__app_name

    @classmethod
    @property
    def icon_open_file(cls) -> QIcon:
        return cls.__icon.open_file

    @classmethod
    @property
    def icon_close_file(cls) -> QIcon:
        return cls.__icon.close_file

    @classmethod
    @property
    def icon_save_file(cls) -> QIcon:
        return cls.__icon.save_file

    @classmethod
    @property
    def icon_save_as_file(cls) -> QIcon:
        return cls.__icon.save_as_file

    @classmethod
    def init(cls, app):
        cls.__icon.open_file = app.style().standardIcon(QStyle.SP_DialogOpenButton)
        cls.__icon.save_file = app.style().standardIcon(QStyle.SP_DialogSaveButton)
        cls.__icon.close_file = app.style().standardIcon(QStyle.SP_DialogCloseButton)
        cls.__icon.save_as_file = app.style().standardIcon(QStyle.SP_DialogSaveAllButton)

    @classmethod
    def read_config(cls):
        settings = QSettings(cls.__file, QSettings.IniFormat)
        settings.beginGroup('Default')
        # 读位置信息
        _pos = settings.value('Position', cls.position)
        cls.position[0] = int(_pos[0])
        cls.position[1] = int(_pos[1])
        # 读大小
        _size = settings.value('Size', cls.size)
        cls.size[0] = int(_size[0])
        cls.size[1] = int(_size[1])
        cls.maximized = settings.value('maximized', cls.maximized)
        settings.endGroup()

        settings.beginGroup('File-Dialog')
        cls.open_path = settings.value('open', cls.open_path)
        cls.save_path = settings.value('save', cls.save_path)
        settings.endGroup()

    @classmethod
    def write_config(cls):
        cls.__write_mutex.lock()
        settings = QSettings(cls.__file, QSettings.IniFormat)
        settings.beginGroup('Default')
        settings.setValue('position', cls.position)
        settings.setValue('size', cls.size)
        settings.setValue('maximized', cls.maximized)
        settings.endGroup()

        settings.beginGroup('File-Dialog')
        settings.setValue('open', cls.open_path)
        settings.setValue('save', cls.save_path)
        settings.endGroup()
        cls.__write_mutex.unlock()

