from loguru import logger as loguru_logger
import logging
import sys,os
import requests


class DingDingNotifier(logging.Handler):
    _session = requests.session()

    def __init__(self, url: str,title:str, **kwargs):
        self.url = url
        self.title = title
        super().__init__(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def emit(self, record):
        """
        Override the :meth:`~logging.Handler.emit` method that takes the ``msg`` attribute from the log record passed

        :param record: :class:`logging.LogRecord`
        """
        message= self.format(record)
        data = {
            "title":self.title,
            "msg":message
        }
        try:
            res = self._session.post(
                url=self.url,
                json=data
            )
        except Exception as e:
            print(e)


class MyLogger:
    def __init__(self,log_all_file,log_error_file):
        self.logger = loguru_logger
        # 清空所有设置
        self.logger.remove()
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               "<cyan>{file}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(log_all_file, level='DEBUG',
                        format='{time:YYYY-MM-DD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               '{file}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        rotation="10 MB",retention="10 days")
        self.logger.add(log_error_file, level='ERROR',
                        format='{time:YYYY-MM-DD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               '{file}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        rotation="10 MB",retention="10 days")
        # dingding_handler = DingDingNotifier("http://easyprint.vip:9090/api/dingtalk/v1/notice", "python_project")
        # self.logger.add(dingding_handler, level="ERROR")

    def get_logger(self):
        return self.logger


RootPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
log_folder = os.path.join(RootPath, "log")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_all_file = os.path.join(log_folder,"all.log")
log_error_file = os.path.join(log_folder,"error.log")

logger = MyLogger(log_all_file,log_error_file).get_logger()
