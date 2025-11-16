import aiosqlite

DB_NAME = 'shop.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                price INTEGER NOT NULL
            )''')
        await db.commit()


async def get_all_products():
    async with aiosqlite.connect(DB_NAME) as db:

        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM products') as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def populate_db():
    products_to_add = [
        (201, 'Razer DeathAdder V3', 'Мышь', 8990),
        (202, 'Logitech G Pro X', 'Клавиатура', 14500),
        (203, 'HyperX Cloud Alpha', 'Гарнитура', 7200)
    ]
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM products') as cursor:
            count = (await cursor.fetchone())[0]

            if count == 0:
                await db.executemany(
                    'INSERT INTO products (id, name, type, price) VALUES (?, ?, ?, ?)',
                    products_to_add
                )
                await db.commit()