from .connection import get_connection

# --- Пользователи ---

def create_user(first_name, middle_name, last_name, email, number_hash, password_hash, password_salt, date_of_birthday):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.users
            (first_name, middle_name, last_name, email, number_hash, password_hash, password_salt, date_of_birthday)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (first_name, middle_name, last_name, email, number_hash, password_hash, password_salt, date_of_birthday)
    )
    conn.commit(); cur.close(); conn.close()


def get_user_by_email(email):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, password_hash, password_salt FROM public.users WHERE email = %s", (email,))
    u = cur.fetchone()
    cur.close(); conn.close()
    return u


def get_user_by_id(user_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, email FROM public.users WHERE id = %s", (user_id,))
    u = cur.fetchone()
    cur.close(); conn.close()
    return u

# --- Категории ---

def get_category(category_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, name FROM public.categories WHERE id = %s", (category_id,))
    c = cur.fetchone()
    cur.close(); conn.close()
    return c

# --- Категории пользователя ---

def add_user_category(user_id, category_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.user_categories (user_id, category_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """,
        (user_id, category_id)
    )
    conn.commit(); cur.close(); conn.close()

# --- Чеки и товары ---

def insert_receipt(user_id, store_id, total_amount, purchase_date, image_path):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.receipts
            (user_id, store_id, total_amount, purchase_date, receipt_image_path)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (user_id, store_id, total_amount, purchase_date, image_path)
    )
    rid = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return rid


def insert_receipt_item(receipt_id, product_name, quantity, price_per_item):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.receipt_items
          (receipt_id, product_name, quantity, price_per_item)
        VALUES (%s,%s,%s,%s)
        """,
        (receipt_id, product_name, quantity, price_per_item)
    )
    conn.commit(); cur.close(); conn.close()

# --- Статистика ---

def get_spending_by_category(user_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.name, SUM(r.total_amount) as total
        FROM public.receipts r
        JOIN public.stores s ON r.store_id = s.id
        JOIN public.categories c ON s.category_id = c.id
        WHERE r.user_id = %s
        GROUP BY c.id, c.name
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_spending_by_month(user_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        SELECT DATE_TRUNC('month', purchase_date) as month, SUM(total_amount)
        FROM public.receipts
        WHERE user_id = %s
        GROUP BY month
        ORDER BY month
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

# --- Магазины и рекомендации ---

def get_all_stores_with_categories():
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.name, c.name as category, c.cashback_percent
        FROM public.stores s
        JOIN public.categories c ON s.category_id = c.id
        """
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def get_store_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name
        FROM stores
        WHERE name ILIKE %s
        LIMIT 1;
    """, (f"%{name}%",))
    
    store = cur.fetchone()
    cur.close()
    conn.close()
    return store

def get_spending_with_cashback(user_id: int):
    """
    Возвращает по каждой категории:
      (category_id, category_name, cashback_percent, total_spent)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
          c.id,
          c.name,
          c.cashback_percent,
          SUM(r.total_amount) AS total_spent
        FROM public.receipts r
        JOIN public.stores s ON r.store_id = s.id
        JOIN public.categories c ON s.category_id = c.id
        WHERE r.user_id = %s
        GROUP BY c.id, c.name, c.cashback_percent
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_top_categories(limit: int = 5):
    """
    Возвращает топ-limit категорий по проценту кешбэка.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, cashback_percent
        FROM public.categories
        ORDER BY cashback_percent DESC
        LIMIT %s
        """,
        (limit,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows  # [(cat_id, name, percent), ...]

    