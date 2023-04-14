import util.Global as gol


def check_can_use_R():
    if not gol.get_value("can_use_r"):
        raise Exception("系统中没有安装R，无法使用关于R的功能")