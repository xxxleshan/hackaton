import os
import json
import psycopg2
import random
import datetime
import secrets
import hashlib
from faker import Faker

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))
DB_NAME = os.getenv('DB_NAME', 'sovkombank')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Demon913133')

conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
cur = conn.cursor()

cur.execute(
    """
    UPDATE public.categories
    SET cashback_percent = %s
    WHERE name = %s;
    """,
    (5.0, "Услуги населению")
)


conn.commit()

cur.close()
conn.close()