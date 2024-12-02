from uuid import UUID
import asyncpg
from database.conn import close_connection_pool, create_connection_pool
from users.models import UserLogin, UserRegister
from errors.auth import UserAlreadyExists, InvalidUser
from errors.errors import InternalError



class UsersDAO():
    async def get_organizations():
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = "SELECT name, id FROM organization"
                rows = await connection.fetch(query)
                results = [dict(row) for row in rows]
            return results

        except Exception as e:
            print(f"An error occurred: {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def get_user(user: str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
            SELECT a.first_name as first_name, a.last_name as last_name, o.name as organization_name
            FROM employee as a
            JOIN organization_responsible as b
            ON a.id=b.user_id
            JOIN organization as o
            ON o.id=b.organization_id
            WHERE a.username=$1

"""
                rows = await connection.fetch(query, user)
                results = [dict(row) for row in rows]
            return results

        except Exception as e:
            print(f"An error occurred: {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def register(data: UserRegister, hashed_password: UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                INSERT INTO employee (username, hashed_password, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """
                query_org = "INSERT INTO organization_responsible(organization_id, user_id) VALUES($1, $2)"
                res = await connection.fetchrow(query, data.username, hashed_password, data.first_name, data.last_name)
                await connection.execute(query_org, data.organization_name, res["id"])

        except Exception as e:
            if e == asyncpg.exceptions.UniqueViolationError:
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
