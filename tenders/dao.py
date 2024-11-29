

import asyncpg

from database.conn import close_connection_pool, create_connection_pool
from errors.errors import InternalError
from errors.response import OK
from tenders.models import NewRequest,TenderStatus, PatchRequest
from uuid import UUID
from errors.tender import TenderNotFound

class TenderDAO():
    async def GetTenders(user:str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at 
                FROM tenders 
                WHERE status='Published' AND employee_username!=$1
                """
                rows = await connection.fetch(query, user)
                results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Ошибка: TenderDao.GetTenders {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def GetTenderBids(user:str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = """SELECT * FROM tenders WHERE id IN (SELECT tender_id FROM bids WHERE status='Published') AND employee_username=$1"""
            async with connection_pool.acquire() as connection:
                rows = await connection.fetch(query, user)
                results = [dict(row) for row in rows]
                return results
        except Exception as e:
            print(f"Ошибка: TenderDao.GetTenders {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def GetTenderVersions(tenderId:UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at 
                FROM tender_versions
                WHERE tender_id=$1
                """
                rows = await connection.fetch(query, tenderId)
                results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Ошибка: TenderDao.GetTenders {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def NewTender(data: NewRequest, user: str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                INSERT INTO tenders (name, description, employee_username)
                VALUES($1, $2, $3) 
                RETURNING id, status,  version, created_at
                """
                query_insert_tender_version = """
                INSERT INTO tender_versions(tender_id, name, description, status, employee_username, version, created_at)
                VALUES($1, $2, $3, $4, $5, $6, $7)
                """
                result = await connection.fetchrow(query, data.name, data.description, user)
                await connection.execute(query_insert_tender_version, result['id'], data.name, data.description, result['status'], user, result['version'], result['created_at'])
                return OK
        except Exception as e:
            print(f"TenderDAO.NewTender {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
    
    async def GetMyTenders(user: str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at FROM tenders
                WHERE employee_username = $1
                """
                result = await connection.fetch(query, user)

                return result
        except Exception as e:
            print(f"TenderDAO.GetMyTenders {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
    
    async def GetTenderStatus(tenderId: UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM tenders WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, tenderId)
                if not result:
                    return TenderNotFound
            async with connection_pool.acquire() as connection:
                query = """
                SELECT status FROM tenders
                WHERE id = $1
                """
                result = await connection.fetchrow(query, tenderId)
                return result
            
        except Exception as e:
            if e==asyncpg.exceptions.NoDataFoundError:
                return TenderNotFound
            print(f"TenderDAO.GetTenderStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def PutTenderStatus(tenderId: UUID, status: TenderStatus):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM tenders WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, tenderId)
                if not result:
                    return TenderNotFound
            async with connection_pool.acquire() as connection:
                query = """
                UPDATE tenders
                SET status = $1
                WHERE id=$2
                """
                await connection.execute(query, status, tenderId)
                result = await UpdateVersion(tenderId)
                if result:
                    return result
                return OK
        except Exception as e:
            print(f"TenderDAO.PutTenderStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def PatchTenderStatus(tenderId: UUID, data: PatchRequest):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM tenders WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, tenderId)
                if not result:
                    return TenderNotFound
            query = "UPDATE tenders SET "
            updates = []
            params = []
            count = 1
            if data.name:
                updates.append(f"name = ${count}")
                params.append(data.name)
                count+=1
            if data.description:
                updates.append(f"description = ${count}")
                params.append(data.description)
                count+=1
            if data.status:
                updates.append(f"status = ${count}")
                params.append(data.status)
                count+=1
            query += ", ".join(updates)
            query += f" WHERE id = ${count}"
            params.append(tenderId)

            async with connection_pool.acquire() as connection:
                await connection.execute(query, *params)
                result = await UpdateVersion(tenderId)
                if result:
                    return result
                return OK
        except Exception as e:
            print(f"TenderDAO.PatchTenderStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def RollbackVersion(tenderId: UUID, version: int):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM tenders WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, tenderId)
                if not result:
                    return TenderNotFound
            query_get = """
            SELECT name, description, status, employee_username FROM tender_versions WHERE tender_id=$1 AND version=$2
            """
            query_set = """
            UPDATE tenders
            SET name=$1, description=$2, status=$3, employee_username=$4
            WHERE id=$5
            """

            async with connection_pool.acquire() as connection:

                result = await connection.fetchrow(query_get, tenderId, version)
                await connection.execute(query_set, result['name'], result['description'], result['status'], result['employee_username'], tenderId)
                result = await UpdateVersion(tenderId)
                if result:
                    return result
                return OK
        except Exception as e:
            print(f"TenderDAO.RollbackVersion {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
    

async def UpdateVersion(tenderId: UUID):
    connection_pool: asyncpg.Pool = await create_connection_pool()
    try:
        query_get = "SELECT id,version,name,description,status,version, employee_username, created_at FROM tenders WHERE id=$1"
        query_set_tender = "UPDATE tenders SET version=$1 WHERE id=$2"
        query_insert_tender_version = """
        INSERT INTO tender_versions(tender_id, name, description, status, employee_username, version, created_at)
        VALUES($1, $2, $3, $4, $5, $6, $7)
        """
        async with connection_pool.acquire() as connection:
            result = await connection.fetchrow(query_get, tenderId)
            version = result['version']
            version+=1
            await connection.execute(query_set_tender, version, tenderId)
            await connection.execute(query_insert_tender_version, result['id'], result['name'], result['description'], result['status'], result['employee_username'], version, result['created_at'])
            
    except Exception as e:
        print(f"TenderDAO.UpdateVersion {e}")
        return InternalError
    finally:
        await close_connection_pool(connection_pool)
