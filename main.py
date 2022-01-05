# This is a sample Python script.
import os
import sys
import main_form
from PySide6 import QtWidgets
from config import Config
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # 读配置文件
    # 获取配置文件路径
    _iniDir = '.'
    if getattr(sys, 'frozen', False):       # exe程序
        _iniDir = os.path.dirname(sys.executable)
    elif __file__:                          # python script
        _iniDir = os.path.dirname(__file__)
    Config.init(_iniDir, app)
    Config.readConfig()

    # 主界面
    widget = main_form.MainForm()

    # 设置主题风格
    if Config.theme != 'None':
        _theme = '%s.xml' % Config.theme
        apply_stylesheet(app, theme=_theme)

    # 显示主界面
    if Config.maximized == 1:
        widget.showMaximized()
    else:
        widget.setGeometry(Config.position[0], Config.position[1], Config.size[0], Config.size[1])
        widget.show()

    sys.exit(app.exec())
