import peewee
from datetime import datetime

database = peewee.SqliteDatabase("Actions.db")


class BaseTable(peewee.Model):
    class Meta:
        database = database


class Actions(BaseTable):
    partner = peewee.CharField()
    name = peewee.CharField()
    start_date = peewee.DateTimeField()
    end_date = peewee.DateTimeField()


database.create_tables([Actions, ])


def add_to_database(partner, name, start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%d.%m.%Y')
    Actions.create(partner=partner,
                   name=name,
                   start_date=start_date,
                   end_date=end_date)


def actions_exists_in_db(name):
    for action in Actions.select():
        return True if action.name == name else False


def delete_expired_actions():
    Actions.delete().where(Actions.end_date < datetime.now()).execute()


add_to_database("Партнер", "Новая акция", "12.12.2020", "12.02.2019")
# delete_expired_actions()
if actions_exists_in_db("Новая акция"):
    print('акция с таким названием есть в базе')
