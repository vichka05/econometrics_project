import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Категории с поддержкой родителя
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                parent_id INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
                    ON DELETE SET NULL,
                UNIQUE (name, parent_id)
            )
            """
        )

        # Товары с привязкой к категории
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT,
                description TEXT,
                price       REAL,
                url         TEXT NOT NULL UNIQUE,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
                    ON DELETE SET NULL
            )
            """
        )

        # Справочник характеристик (типы)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS characteristics (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                unit TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS product_characteristics (
                product_id        INTEGER NOT NULL,
                characteristic_id INTEGER NOT NULL,
                value             TEXT NOT NULL,

                PRIMARY KEY (product_id, characteristic_id),

                FOREIGN KEY (product_id) REFERENCES products(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (characteristic_id) REFERENCES characteristics(id)
                    ON DELETE CASCADE
            )
            """
        )

        conn.commit()


def upsert_product(name, price, url, category_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO products (name, price, url, category_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                name = excluded.name,
                price = excluded.price,
                category_id = excluded.category_id
            """,
            (name, price, url, category_id),
        )
        conn.commit()


def add_product_description(product_id, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET description = ?
            WHERE id = ?
            """,
            (description, product_id),
        )
        conn.commit()


def ensure_category_path(category_names):
    parent_id = 0
    last_id = 0

    for name in category_names:
        last_id = upsert_category(name, parent_id)
        parent_id = last_id
    return last_id


def upsert_category(name, parent_id=0):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO categories (name, parent_id)
            VALUES (?, ?)
            ON CONFLICT(name, parent_id) DO NOTHING
            """,
            (name, parent_id),
        )
        conn.commit()

        cursor.execute(
            """
            SELECT id FROM categories
            WHERE name = ? AND (parent_id IS ? OR parent_id = ?)
            """,
            (name, parent_id, parent_id),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def update_product_category(product_id, category_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET category_id = ? WHERE id = ?",
            (category_id, product_id)
        )
        conn.commit()


def upsert_characteristic(name, unit=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO characteristics (name, unit)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
            """,
            (name, unit),
        )
        conn.commit()

        cursor.execute(
            """
            SELECT id FROM characteristics
            WHERE name = ?
            """,
            (name,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def add_product_characteristic(product_id, characteristic_id, value):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO product_characteristics (product_id, characteristic_id, value)
            VALUES (?, ?, ?)
            ON CONFLICT(product_id, characteristic_id) DO UPDATE SET
                value = excluded.value
            """,
            (product_id, characteristic_id, value),
        )
        conn.commit()


def get_all_products():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, id FROM products")
        return cursor.fetchall()
