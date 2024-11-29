import asyncio
import asyncpg
from config import DB_CONFIG


async def create_connection_pool() -> asyncpg.Pool:
    connection_pool: asyncpg.Pool = await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=1,
        max_size=10,
    )
    print("pool created")
    return connection_pool


async def close_connection_pool( connection_pool: asyncpg.Pool):
    # Закрытие пула соединений
    await connection_pool.close()
    print("Connection pool closed.")

class DB:
    @classmethod
    async def init_tables(cls):
        connection_pool = await create_connection_pool()
        # Путь к вашему DDL-файлу
        ddl_file_path = 'migrations/ddl.sql'
        try:
            # Чтение DDL-скрипта
            with open(ddl_file_path, 'r') as file:
                ddl_script = file.read()

            # Выполнение DDL-скрипта
            async with connection_pool.acquire() as connection:
                await connection.execute(ddl_script)
                print("DDL script executed successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await close_connection_pool(connection_pool=connection_pool)
