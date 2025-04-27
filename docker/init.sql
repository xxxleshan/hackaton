CREATE TABLE public.categories
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cashback_percent FLOAT NOT NULL,
    icon_path VARCHAR(255) -- Путь или имя файла иконки
);

ALTER TABLE IF EXISTS public.categories
    OWNER TO postgres;


CREATE TABLE public.stores
(
    id           SERIAL PRIMARY KEY,            -- уникальный идентификатор магазина
    category_id  INTEGER NOT NULL,              -- ссылка на категорию магазина
    name         VARCHAR(255) NOT NULL,         -- название магазина
    logo_path    TEXT    NOT NULL,              -- локальный путь к логотипу

    CONSTRAINT fk_stores_category
        FOREIGN KEY (category_id)
        REFERENCES public.categories (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

ALTER TABLE IF EXISTS public.stores
    OWNER TO postgres;
    

CREATE TABLE public.users
(
    id                SERIAL PRIMARY KEY,               -- Уникальный идентификатор пользователя
    first_name        VARCHAR(100)    NOT NULL,         -- Имя
    middle_name       VARCHAR(100),                    -- Отчество (может быть NULL)
    last_name         VARCHAR(100)    NOT NULL,         -- Фамилия
    email             VARCHAR(255)    UNIQUE NOT NULL,  -- Электронная почта
    number_hash       TEXT            UNIQUE NOT NULL,  -- Хеш телефонного номера
    password_hash     TEXT            NOT NULL,         -- Хеш пароля
    password_salt     TEXT            NOT NULL,         -- Соль для хеша пароля
    date_of_birthday  DATE            NOT NULL,         -- Дата рождения
    avatar_path       VARCHAR(255)                      -- Путь к аватарке пользователя (локальный файл)
);

ALTER TABLE IF EXISTS public.users
    OWNER TO postgres;

-- Таблица отсканированных чеков
CREATE TABLE IF NOT EXISTS public.receipts
(
    id SERIAL PRIMARY KEY,                        -- Уникальный идентификатор чека
    user_id INTEGER NOT NULL,                      -- Кто загрузил чек (ссылка на пользователя)
    store_id INTEGER,                              -- Магазин (если удалось определить, необязательное поле)
    total_amount NUMERIC(10,2) NOT NULL,            -- Общая сумма покупки
    purchase_date TIMESTAMP NOT NULL,              -- Дата покупки
    receipt_image_path TEXT,                       -- Путь к изображению чека (если нужно сохранить)
    created_at TIMESTAMP DEFAULT NOW(),            -- Когда чек был загружен в систему

    CONSTRAINT fk_receipts_user
        FOREIGN KEY (user_id)
        REFERENCES public.users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_receipts_store
        FOREIGN KEY (store_id)
        REFERENCES public.stores (id)
        ON DELETE SET NULL
);

ALTER TABLE IF EXISTS public.receipts
    OWNER TO postgres;

-- Таблица товаров, привязанных к конкретному чеку
CREATE TABLE IF NOT EXISTS public.receipt_items
(
    id SERIAL PRIMARY KEY,                     -- Уникальный идентификатор товара в чеке
    receipt_id INTEGER NOT NULL,                -- Ссылка на чек (кому принадлежит товар)
    product_name VARCHAR(255) NOT NULL,         -- Название товара
    quantity INTEGER DEFAULT 1,                 -- Количество (если доступно)
    price_per_item NUMERIC(10,2) NOT NULL,       -- Цена за единицу товара

    CONSTRAINT fk_receipt_items_receipt
        FOREIGN KEY (receipt_id)
        REFERENCES public.receipts (id)
        ON DELETE CASCADE
);

ALTER TABLE IF EXISTS public.receipt_items
    OWNER TO postgres;


CREATE TABLE IF NOT EXISTS public.user_categories
(
    user_id     INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES public.categories(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, category_id)
);