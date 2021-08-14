from helpers.ActionsUtil import ActionsUtil
from helpers.CsvUtil import CsvUtil
from helpers.DateUtil import DateUtil


class Utils:

    def __init__(self, queue=None):
        self.DATE_UTIL = DateUtil()
        self.CSV_UTIL = CsvUtil()
        self.ACTIONS_UTIL = ActionsUtil(queue)

    def exception_hook(stlf, exctype, value, tb):
        """Переопределяем вывод ошибок"""
        print("*******ERROR********")
        print('My Error Information')
        print('Type:', exctype)
        print('Value:', value)
        print('Traceback:', tb)
        print("*******ERROR********")
