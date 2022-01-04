# This is a sample Python script.
import sys
import main_form
from PySide6 import QtWidgets
from config import Config

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # 读配置文件
    Config.init(app)
    Config.read_config()

    # 主界面
    widget = main_form.MainForm()
    if Config.maximized:
        widget.showMaximized()
    else:
        widget.setGeometry(Config.position[0], Config.position[1], Config.size[0], Config.size[1])
        widget.show()

    sys.exit(app.exec())