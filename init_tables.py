
import asyncio

from database.conn import DB


asyncio.run(DB.init_tables())