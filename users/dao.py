import asyncpg
from database.conn import DB, close_connection_pool, create_connection_pool
from users.models import UserLogin, UserRegister
from errors.auth import UserAlreadyExists, InvalidUser
from errors.errors import InternalError
from errors.response import OK

import logging

class UsersDAO():
    async def register(data: UserRegister, hashed_password: str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                INSERT INTO employee (username, hashed_password, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                """
                await connection.execute(query, data.username, hashed_password, data.first_name, data.last_name)
        except Exception as e:
            if e==asyncpg.exceptions.UniqueViolationError:
                return UserAlreadyExists
            else:
                print(f"An error occurred: {e}")
                return InternalError
        finally:
            await close_connection_pool(connection_pool)
        

    async def login(data: UserLogin):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT hashed_password FROM employee WHERE username = $1
                """
                result = await connection.fetchrow(query, data.username)
                if result is None:
                    return InvalidUser
                else:
                    return result['hashed_password']
        except Exception as e:
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
