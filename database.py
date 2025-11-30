import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_NAME = 'catalog.db'


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT
            )
        """)
        await db.commit()
        logger.info("Database initialized successfully.")


async def populate_db():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM products")
        count = (await cursor.fetchone())[0]

        if count == 0:
            initial_products = [
                (101, 'Razer DeathAdder V3 Pro', 'Мышь', 8990, 'Легкая беспроводная мышь для киберспорта.'),
                (102, 'Logitech G Pro X', 'Клавиатура', 14500,
                 'Механическая клавиатура TKL с быстрыми переключателями.'),
                (103, 'HyperX Cloud Alpha', 'Гарнитура', 7200,
                 'Проводная гарнитура с двойными камерами для чистого звука.'),
                (104, 'SteelSeries Apex Pro Mini', 'Клавиатура', 19990,
                 'Компактная 60% клавиатура с регулируемыми механическими переключателями.'),
                (105, 'Razer BlackShark V2', 'Гарнитура', 6500,
                 'Легкая проводная гарнитура с пассивным шумоподавлением.'),
                (106, 'Logitech G305 K/DA', 'Мышь', 3500, 'Беспроводная мышь с сенсором HERO и ярким дизайном.'),
                (107, 'Logitech G440', 'Коврик', 1500,
                 'Твердый игровой коврик для мыши, обеспечивающий высокое скольжение.'),
            ]

            await db.executemany(
                "INSERT INTO products (id, name, type, price, description) VALUES (?, ?, ?, ?, ?)",
                initial_products
            )
            await db.commit()
            logger.info("Database populated with initial data.")
        else:
            logger.info(f"Database already contains {count} items. Skipping population.")


async def get_all_products():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products ORDER BY id")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_product_by_id(product_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_product(name: str, type: str, price: int, description: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO products (name, type, price, description) VALUES (?, ?, ?, ?)",
            (name, type, price, description)
        )
        await db.commit()
        return cursor.lastrowid