import re
from calendar import monthrange
from datetime import datetime, timedelta


class DateUtil:
    """Даты для преобразования 02 февраля в 02.02 и тд."""
    MONTH_NAME = {"01": "янв", "02": "фев", "03": "мар", "04": "апр",
                  "05": "мая", "06": "июн", "07": "июл", "08": "авг",
                  "09": "сен", "10": "окт", "11": "ноя", "12": "дек", }
    DATA_NOW = datetime.now().strftime('%d.%m.%Y')

    def one_date_return_two(self, incoming_date):
        """ принимает дату в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 и до конца месяца """
        day, month, year = incoming_date.split(" ")
        month = self.convert_month_name(month)
        date_start = datetime(day=int(day), month=month, year=int(year)).strftime('%d.%m.%Y')
        day_on_month = monthrange(year=int(year), month=month)
        end_data = datetime(day=day_on_month[1], month=month, year=int(year)).strftime('%d.%m.%Y')
        return date_start, end_data

    def convert_text_date(self, incoming_date):
        """ принимает текст с датами в формате '01.12.21 по 31.03.21' Возвращает 2 даты начала и окончания"""
        date = re.findall(r'\d+\.\d+\.*\d*', incoming_date)
        start = self.get_one_date(date[0])
        end = self.get_one_date(date[1])
        return start, end

    def get_double_date(self, first, second):
        """ принимает 2 даты в формате 1 февраля 2019, возвращает 2 даты в формате 01.02.2019 03.02.2019 """
        try:
            first = self.get_one_date(first)
        except AttributeError:
            first = self.DATA_NOW
        try:
            second = self.get_one_date(second)
        except AttributeError:
            second = datetime.strptime(first, '%d.%m.%Y')
            day_on_month = monthrange(year=int(second.year), month=int(second.month))
            second = datetime(day=day_on_month[1], month=second.month, year=second.year).strftime('%d.%m.%Y')
        return first, second

    def get_one_date(self, text):
        """ принимает 1 дату в формате 1 февраля 2019 или 1 февраля, возвращает 1 дату в формате 01.02.2019"""
        flag = False
        try:
            text = re.search(r'(\d+\s\w+\s?\d*)', text).group(1)
        except AttributeError:
            text = re.search(r'(\d+.\w+.\d*)', text).group(1)
            text = text.replace('.', ' ')
        text = re.sub(r'\xa0', ' ', text).strip()
        try:
            day, month, year = text.split(' ')
        except ValueError:
            day, month = text.split(" ")
            year = datetime.now().year
            flag = True
        month = self.convert_month_name(month)
        date = datetime(day=int(day), month=int(month), year=int(year))
        if flag:
            if (date - datetime.now()).days > 200:
                if datetime.now().month > 6:
                    date = datetime(day=int(day), month=month, year=int(year) + 1)
                else:
                    date = datetime(day=int(day), month=month, year=int(year) - 1)
        return date.strftime('%d.%m.%Y')

    def get_date_plus_days(self, count):
        """ Прибавляет к текущей дате count дней"""
        date_now = datetime.strptime(self.DATA_NOW, '%d.%m.%Y')
        date = date_now + timedelta(days=count)
        return date.strftime('%d.%m.%Y')

    def get_date_now_to_end_month(self):
        """Возвращает start с текущего дня и end  конец текущего месяца"""
        date_start = self.DATA_NOW
        date_end = datetime.strptime(date_start, '%d.%m.%Y')
        day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
        date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
        return date_start, date_end

    def get_date_end_month(self):
        """Возвращает дату на конец текущего месяца"""
        date_end = datetime.strptime(self.DATA_NOW, '%d.%m.%Y')
        day_on_month = monthrange(year=int(date_end.year), month=int(date_end.month))
        date_end = datetime(day=day_on_month[1], month=date_end.month, year=date_end.year).strftime('%d.%m.%Y')
        return date_end

    def get_first_day_month(self):
        """Возвращает первый день текущего месяца"""
        date_start = datetime.strptime(self.DATA_NOW, '%d.%m.%Y')
        date_start = datetime(day=1, month=date_start.month, year=date_start.year).strftime('%d.%m.%Y')
        return date_start

    def get_date_month_ahead(self, start):
        """Возвращает дату через 30 дней после даты начала"""
        date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=30)
        return date_end.strftime('%d.%m.%Y')

    def get_date_half_year_ahead(self, start):
        """Возвращает дату через полгода после даты начала"""
        date_end = datetime.strptime(start, '%d.%m.%Y') + timedelta(days=179)
        return date_end.strftime('%d.%m.%Y')

    def promotion_is_outdated(self, end):
        """Проверяет кончилась ли акция"""
        date_end = datetime.strptime(end, '%d.%m.%Y')
        date_now = datetime.strptime(self.DATA_NOW, '%d.%m.%Y')
        return False if date_end >= date_now else True

    def get_range_date(self, text):
        """ возвращает список [начало акции, конец акции] ищет текст в формате 1 по 20 февраля 2019 или 1 по 20 февраля"""
        try:
            text = re.search(r'(\d+\sпо\s\d+\s\w+\s\d*)', text).group(1).strip()
            data = text.split('по')
        except AttributeError:
            try:
                text = re.search(r'(\d+\sи\s\d+\s\w+\s\d*)', text).group(1).strip()
                data = text.split('и')
            except AttributeError:
                try:
                    text = re.search(r'(\d+\s\w+\s\d*.*по\s\d+\s\w+\s\d*)', text).group(1).strip()
                    data = text.split('по')
                except AttributeError:
                    text = re.search(r'(\d+-\d+\s\w+\s\d*)', text).group(1).strip()
                    data = text.split('-')
        return data

    def get_do_period(self, text):
        """ Принимает текст в формате 'До 1 декабря', возвращает дату начала - сегодня, дату окончания 01.12.2020"""
        start = datetime.now()
        result = re.search(r'(\d+)\s([а-яА-Я]+)\s?(\d{4})?', text)
        day = result.group(1).strip()
        month = result.group(2).strip().lower()
        month = self.convert_month_name(month)
        year = result.group(3).strip() if result.lastindex > 2 else start.year
        end = datetime(day=int(day), month=month, year=int(year)).strftime('%d.%m.%Y')
        return start.strftime('%d.%m.%Y'), end



    def convert_list_to_date(self, my_list):
        """принимает не отформатированный список [дата начала, дата окончания] [1, 20 февраля] [1 марта, 20 марта 2020]"""
        end = self.get_one_date(my_list[1])
        start = my_list[0].strip().split(' ')
        if len(start) == 1:
            start_temp = datetime.strptime(end, '%d.%m.%Y')
            start = datetime(day=int(start[0]), month=start_temp.month, year=start_temp.year).strftime('%d.%m.%Y')
        else:
            start = ' '.join(start)
            start = self.get_one_date(start)
        return start, end

    def get_start_date_in_date(self, text, flag):
        """ Принимает текст, ищет даты в формате 20 февраля 2019 или 20 февраля, возвращает дату начала и конец месяца"""
        start = re.search(r'(\d+\s\w+(\s\d{4})?)', text).group(1).strip()
        start = self.get_one_date(start)
        end = self.get_date_end_month()
        if flag:
            return start, end
        else:
            return start

    def search_data_in_text(self, text):
        """ Принимает текст, ищет 2 даты в формате 20.12.2020 или в формате 20 декабря 2020 по 25 декабря 2020 и
        вовзращает их как старт и конец """
        try:
            income_data = re.findall(r'(\d+.\d+.\d+)', text)
            start = income_data[0]
            end = income_data[1]
        except:
            income_data = re.findall(r'(\d+.\d+)', text)
            start = self.get_one_date(income_data[0])
            end = self.get_one_date(income_data[1])
        return start, end

    def search_end_data_in_text(self, text):
        """ Принимает текст, ищет 2 даты в формате 20.12.2020 или в формате 20 декабря 2020 по 25 декабря 2020 и
        вовзращает их как старт и конец """
        start = self.DATA_NOW
        try:
            income_data = re.findall(r'(\d+.\d+.\d+)', text)
            end = income_data[0]
        except:
            income_data = re.findall(r'(\d+.\d+)', text)
            end = self.get_one_date(income_data[0])
        return start, end

    def search_data_in_text_without_year(self, text):
        """ Принимает текст, ищет 2 даты в формате 20.12 или в формате 20 декабря по 25 декабря, добавляет текущий год
        и вовзращает их как старт и конец """
        income_data = re.findall(r'(\d+.\d+)', text)
        start = income_data[0] + '.' + str(datetime.now().year)
        end = income_data[1] + '.' + str(datetime.now().year)
        return start, end

    def convert_month_name(self, month):
        for num, name in self.MONTH_NAME.items():
            if name in month.lower():
                month = int(num)
                break
        return month
