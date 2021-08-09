from helpers.ActionsUtil import ActionsUtil
from helpers.CsvUtil import CsvUtil
from helpers.DateUtil import DateUtil


class Utils:

    def __init__(self, queue):
        self.DATE_UTIL = DateUtil()
        self.CSV_UTIL = CsvUtil()
        self.ACTIONS_UTIL = ActionsUtil(queue)
