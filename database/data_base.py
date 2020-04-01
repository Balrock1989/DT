from collections import defaultdict
from pprint import pprint

import peewee
from datetime import datetime

from helpers.helper import database_path

database = peewee.SqliteDatabase(database_path)
# database = peewee.SqliteDatabase("database/Actions.db")



class BaseTable(peewee.Model):
    class Meta:
        database = database


class Actions(BaseTable):
    partner = peewee.CharField()
    name = peewee.CharField()
    start_date = peewee.DateTimeField()
    end_date = peewee.DateTimeField()
    last_update = peewee.DateTimeField()


def create_database():
    database.create_tables([Actions, ])


def add_to_database(partner, name, start_date, end_date, last_update=None):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%d.%m.%Y')
    last_update = datetime.strptime(last_update, '%d.%m.%Y') if isinstance(last_update, str) else datetime.now()
    Actions.create(partner=partner,
                   name=name,
                   start_date=start_date,
                   end_date=end_date,
                   last_update=last_update)


def check_actions_on_name(name):
    for action in Actions.select():
        if action.name == name:
            return True


def delete_expired_actions():
    print(f'Было удалено устаревших акций: {Actions.delete().where(Actions.end_date < datetime.now()).execute()}')


def show_expired_actions():
    partner = Actions.select().where(Actions.end_date < datetime.now()).get().partner
    name = Actions.select().where(Actions.end_date < datetime.now()).get().name
    start_date = Actions.select().where(Actions.end_date < datetime.now()).get().start_date.strftime('%d.%m.%Y')
    end_date = Actions.select().where(Actions.end_date < datetime.now()).get().end_date.strftime('%d.%m.%Y')
    print(f'Акция устарела: {partner}: {name}, {start_date} - {end_date}')


def print_stat(queue):
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
    for row in Actions.select().tuples():
        row = list(row)
        row[3] = row[3].strftime('%d.%m.%Y')
        row[4] = row[4].strftime('%d.%m.%Y')
        row[5] = row[5].strftime('%d.%m.%Y')
        print(*row)


def actions_exists_in_db(partner, name, start_date, end_date):
    if check_actions_on_name(name) is None:
        add_to_database(partner, name, start_date, end_date)
        return False
    else:
        print('акция с таким названием есть в базе')
        return True


def clear_partner_info(partner):
    print(f'Было удалено {Actions.delete().where(Actions.partner == partner).execute()} акций для партнера {partner}')


# clear_partner_info("Утконос")
# show_actions()