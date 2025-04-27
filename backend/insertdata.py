import os
import json
import psycopg2
import random
import datetime
import secrets
import hashlib
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

# Конфигурация подключения к базе
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))
DB_NAME = os.getenv('DB_NAME', 'sovkombank')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Demon913133')

# Путь к файлу stores.json (предполагается, что скрипт запускается из корня проекта)
stores_json_path = os.path.join(os.getcwd(), "testdata",'stores.json')

# Количество тестовых пользователей и чеков на пользователя
NUM_USERS = 10
MIN_RECEIPTS_PER_USER = 1
MAX_RECEIPTS_PER_USER = 5
MIN_ITEMS_PER_RECEIPT = 1
MAX_ITEMS_PER_RECEIPT = 5


def main():
    # Подключаемся к БД
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Очищаем таблицы
    cur.execute("TRUNCATE public.receipt_items, public.receipts, public.users, public.stores, public.categories, public.user_categories RESTART IDENTITY CASCADE;")
    conn.commit()

    # Загружаем данные магазинов из JSON
    with open(stores_json_path, encoding='utf-8') as f:
        stores_data = json.load(f)

    # Вставляем категории (уникальные) с cashback_percent=0
    categories = {item['категория'] for item in stores_data}
    category_map = {}
    for cat in categories:
        cur.execute(
            "INSERT INTO public.categories (name, cashback_percent) VALUES (%s, %s) RETURNING id",
            (cat, 0.0)
        )
        cat_id = cur.fetchone()[0]
        category_map[cat] = cat_id
    conn.commit()

    # Вставляем магазины
    store_map = {}
    for item in stores_data:
        name = item['название']
        cat = item['категория']
        logo = item.get('картинка')
        cat_id = category_map[cat]
        cur.execute(
            "INSERT INTO public.stores (category_id, name, logo_path) VALUES (%s, %s, %s) RETURNING id",
            (cat_id, name, logo)
        )
        store_id = cur.fetchone()[0]
        store_map[name] = store_id
    conn.commit()

    # Создаем фейк-генератор
    fake = Faker('ru_RU')

    # Вставляем пользователей
    user_ids = []
    for _ in range(NUM_USERS):
        first = fake.first_name()
        middle = fake.middle_name() if random.random() < 0.7 else None
        last = fake.last_name()
        email = fake.unique.email()
        phone = fake.phone_number()
        number_hash = hashlib.sha256(phone.encode()).hexdigest()
        salt = secrets.token_hex(16)
        password = fake.password(length=10)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=70)
        cur.execute(
            """
            INSERT INTO public.users
                (first_name, middle_name, last_name, email, number_hash, password_hash, password_salt, date_of_birthday)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            (first, middle, last, email, number_hash, password_hash, salt, dob)
        )
        uid = cur.fetchone()[0]
        user_ids.append(uid)
    conn.commit()

    # Вставляем чеки и товары
    for uid in user_ids:
        num_receipts = random.randint(MIN_RECEIPTS_PER_USER, MAX_RECEIPTS_PER_USER)
        for _ in range(num_receipts):
            store_id = random.choice(list(store_map.values()))
            purchase_date = fake.date_time_between(start_date='-1y', end_date='now')
            # Генерируем товары
            num_items = random.randint(MIN_ITEMS_PER_RECEIPT, MAX_ITEMS_PER_RECEIPT)
            items = []
            total_amount = 0.0
            for _ in range(num_items):
                product = fake.word().capitalize()
                qty = random.randint(1, 3)
                price = round(random.uniform(50, 2000), 2)
                items.append((product, qty, price))
            # Вставляем чек
            cur.execute(
                """
                INSERT INTO public.receipts
                    (user_id, store_id, total_amount, purchase_date, receipt_image_path)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (uid, store_id, total_amount, purchase_date, None)
            )
            receipt_id = cur.fetchone()[0]
            # Вставляем позиции товаров
            for product, qty, price in items:
                cur.execute(
                    """
                    INSERT INTO public.receipt_items
                      (receipt_id, product_name, quantity, price_per_item)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (receipt_id, product, qty, price)
                )
    conn.commit()

    # Закрываем соединение
    cur.close()
    conn.close()

    print("✅ Database populated with test data")


if __name__ == '__main__':
    main()
