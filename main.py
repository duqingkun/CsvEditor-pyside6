# This is a sample Python script.
import sys
import main_form
from PySide6 import QtWidgets
from config import Config
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # 读配置文件
    Config.init(app)
    Config.readConfig()

    # 主界面
    widget = main_form.MainForm()

    # 设置主题风格
    apply_stylesheet(app, theme='light_yellow.xml')

    # 显示主界面
    if Config.maximized == 1:
        widget.showMaximized()
    else:
        widget.setGeometry(Config.position[0], Config.position[1], Config.size[0], Config.size[1])
        widget.show()

    sys.exit(app.exec())
