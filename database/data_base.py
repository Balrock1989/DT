import peewee
from datetime import datetime, timedelta

from helpers.Paths import DATABASE_PATH

database = peewee.SqliteDatabase(DATABASE_PATH, timeout=3, pragmas={'journal_mode': 'wal'})


class BaseTable(peewee.Model):
    class Meta:
        database = database


class Actions(BaseTable):
    """Генерация таблицы"""
    partner = peewee.CharField()
    name = peewee.CharField()
    start_date = peewee.DateTimeField()
    end_date = peewee.DateTimeField()
    last_update = peewee.DateTimeField()


def create_database():
    """Создание таблиц, если их еще нет"""
    database.create_tables([Actions, ])


def add_to_database(partner, name, start_date, end_date, last_update=None):
    """Добавление новой записи в БД"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%d.%m.%Y')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    last_update = datetime.strptime(last_update, '%d.%m.%Y') if isinstance(last_update, str) else datetime.now()
    Actions.create(partner=partner,
                   name=name,
                   start_date=start_date,
                   end_date=end_date,
                   last_update=last_update)


def check_actions_on_name(name):
    """Проверка, существует ли акция с таким именем в базе"""
    for action in Actions.select():
        if action.name == name:
            return True


def delete_expired_actions(queue):
    """Удаление акций если дата окончания уже прошла"""
    queue.put(
        f'Было удалено устаревших акций из БД: {Actions.delete().where(Actions.end_date < datetime.now()).execute()}')


def show_expired_actions():
    """Вывести на экран устаревшие акции"""
    try:
        yesterday = datetime.now()-timedelta(days=2)
        partner = Actions.select().where(Actions.end_date < yesterday).get().partner
        name = Actions.select().where(Actions.end_date < datetime.now()).get().name
        start_date = Actions.select().where(Actions.end_date < datetime.now()).get().start_date.strftime('%d.%m.%Y')
        end_date = Actions.select().where(Actions.end_date < datetime.now()).get().end_date.strftime('%d.%m.%Y')
        print(f'Акция устарела: {partner}: {name}, {start_date} - {end_date}')
    except:
        pass

def print_stat(queue):
    """Вывод статистики последнего обновления на экран"""
    try:
        query = Actions.select(Actions.partner, Actions.last_update).order_by(Actions.last_update)
        statistics = {}
        for distinct_ts in query.tuples():
            statistics[distinct_ts[0]] = distinct_ts[1].strftime('%d.%m.%Y')
        for partner, end_date in statistics.items():
            queue.put(f'Партнер: {partner} , последнее обновление {end_date}')
    except:
        queue.put('База данных пуста')


def show_actions():
    """Вывести на экран все существующие акции в БД"""
    for row in Actions.select().tuples():
        row = list(row)
        row[3] = row[3].strftime('%d.%m.%Y')
        row[4] = row[4].strftime('%d.%m.%Y')
        row[5] = row[5].strftime('%d.%m.%Y')
        print(*row)


def actions_exists_in_db(partner, name, start_date, end_date):
    """Если акции нет в базе то добавляем ее"""
    if check_actions_on_name(name) is None:
        add_to_database(partner, name, start_date, end_date)
        return False
    else:
        print('акция с таким названием есть в базе')
        return True

def actions_exists_in_db_new(action):
    """Если акции нет в базе то добавляем ее"""
    if check_actions_on_name(action.name) is None:
        add_to_database(action.partner_name, action.name, action.start, action.end)
        return False
    else:
        print('акция с таким названием есть в базе')
        return True


def clear_partner_info(partner):
    """Удалить все записи по партнеру"""
    print(f'Было удалено {Actions.delete().where(Actions.partner == partner).execute()} акций для партнера {partner}')
