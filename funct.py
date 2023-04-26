from data import db_session
from data.categories import Category


def add_categories():
    data = ['Личные вещи', 'Транспорт', 'Недвижимость',
            'Услуга', 'Электроника', 'Бытовая техника',
            'Для дома и дачи', 'Спорт и отдых',
            'Хобби и развлечения', 'Животные', 'Хендмейд']
    for info in data:
        catg = Category()
        catg.name_category = info
        db_sess = db_session.create_session()
        db_sess.add(catg)
        db_sess.commit()