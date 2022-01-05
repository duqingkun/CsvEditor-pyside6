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
    OpenFile = None
    CloseFile = None
    SaveFile = None
    SaveAsFile = None


class Config(object):
    # 可读写配置项
    position = [0, 0]  # 窗体初始位置（左上角x y坐标）
    size = [800, 600]  # 窗体初始大小（width,height）
    maximized = False  # 是否最大化显示
    openPath = '.'
    savePath = '.'

    # 私有属性
    __file = 'config.ini'
    __writeMutex = QMutex()
    __icon = Icon()
    __appName = 'CSV Editor'

    # 只读配置项
    @classmethod
    @property
    def appName(cls):
        return cls.__appName

    @classmethod
    @property
    def iconOpenFile(cls) -> QIcon:
        return cls.__icon.OpenFile

    @classmethod
    @property
    def iconCloseFile(cls) -> QIcon:
        return cls.__icon.CloseFile

    @classmethod
    @property
    def iconSaveFile(cls) -> QIcon:
        return cls.__icon.SaveFile

    @classmethod
    @property
    def iconSaveAsFile(cls) -> QIcon:
        return cls.__icon.SaveAsFile

    @classmethod
    def init(cls, app):
        cls.__icon.OpenFile = app.style().standardIcon(QStyle.SP_DialogOpenButton)
        cls.__icon.SaveFile = app.style().standardIcon(QStyle.SP_DialogSaveButton)
        cls.__icon.CloseFile = app.style().standardIcon(QStyle.SP_DialogCloseButton)
        cls.__icon.SaveAsFile = app.style().standardIcon(QStyle.SP_DialogSaveAllButton)

    @classmethod
    def readConfig(cls):
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
        cls.openPath = settings.value('open', cls.openPath)
        cls.savePath = settings.value('save', cls.savePath)
        settings.endGroup()

    @classmethod
    def writeConfig(cls):
        cls.__writeMutex.lock()
        settings = QSettings(cls.__file, QSettings.IniFormat)
        settings.beginGroup('Default')
        settings.setValue('position', cls.position)
        settings.setValue('size', cls.size)
        settings.setValue('maximized', cls.maximized)
        settings.endGroup()

        settings.beginGroup('File-Dialog')
        settings.setValue('open', cls.openPath)
        settings.setValue('save', cls.savePath)
        settings.endGroup()
        cls.__writeMutex.unlock()

