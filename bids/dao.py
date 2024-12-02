import asyncpg

from database.conn import close_connection_pool, create_connection_pool
from errors.errors import InternalError
from errors.response import OK
from bids.models import NewRequest,BidStatus, PatchRequest
from uuid import UUID
from errors.bids import BidNotFound

class BidDAO():
    async def GetBidsApproved(user:str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT a.id as tender_id, a.name as tender_name, a.description as tender_description, a.status as tender_status, b.id as bid_id, b.name as bid_name, b.description as bid_description, b.status as bid_status
                FROM tenders as a
                JOIN bids as b
                ON a.id=b.tender_id
                WHERE b.employee_username = $1 AND a.status='Closed' AND b.status='Approved'
                """
                rows = await connection.fetch(query, user)
                results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Ошибка: BidDAO.GetBidsApproved {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
            
    async def GetBids(tenderId: UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at, tender_id
                FROM bids
                WHERE tender_id = $1 AND status='Published'
                """
                rows = await connection.fetch(query, tenderId)
                results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Ошибка: BidDAO.GetBids {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def GetBidVersions(bidId:UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at 
                FROM bid_versions
                WHERE bid_id=$1
                """
                rows = await connection.fetch(query, bidId)
                results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Ошибка: BidDAO.GetBidVersions {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)


    async def NewBid(data: NewRequest, user:str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                INSERT INTO bids (name, description, employee_username, tender_id)
                VALUES($1, $2, $3, $4) 
                RETURNING id, status,  version, created_at
                """
                query_insert_bid_version = """
                INSERT INTO bid_versions(bid_id, name, description, status, employee_username, version, created_at, tender_id)
                VALUES($1, $2, $3, $4, $5, $6, $7, $8)
                """
                result = await connection.fetchrow(query, data.name, data.description, user, data.tenderId)
                await connection.execute(query_insert_bid_version, result['id'], data.name, data.description, result['status'], user, result['version'], result['created_at'], data.tenderId)
                return OK
        except Exception as e:
            print(f"BidDAO.NewBid {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
    
    async def GetMyBid(user: str):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            async with connection_pool.acquire() as connection:
                query = """
                SELECT id, name, description, status, version, created_at, tender_id FROM bids
                WHERE employee_username = $1
                """
                result = await connection.fetch(query, user)

                return result
        except Exception as e:
            print(f"BidDAO.GetMyBid {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)
    
    async def GetBidStatus(bidId: UUID):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM bids WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, bidId)
                if not result:
                    return BidNotFound
            async with connection_pool.acquire() as connection:
                query = """
                SELECT status FROM bids
                WHERE id = $1
                """
                result = await connection.fetchrow(query, bidId)
                return result
            
        except Exception as e:
            print(f"BidDAO.GetBidStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def PutBidStatus(bidId: UUID, status: BidStatus):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM bids WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, bidId)
                if not result:
                    return BidNotFound
            async with connection_pool.acquire() as connection:
                query = """
                UPDATE bids
                SET status = $1
                WHERE id=$2
                """
                await connection.execute(query, status, bidId)
                result = await UpdateVersion(bidId)
                if result:
                    return result
                return OK
        except Exception as e:
            print(f"BidDAO.PutbidStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def RollbackVersion(bidId: UUID, version: int):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM bids WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, bidId)
                if not result:
                    return BidNotFound
            query_get = """
            SELECT name, description, status, employee_username FROM bid_versions WHERE bid_id=$1 AND version=$2
            """
            query_set = """
            UPDATE bids
            SET name=$1, description=$2, status=$3, employee_username=$4
            WHERE id=$5
            """

            async with connection_pool.acquire() as connection:

                result = await connection.fetchrow(query_get, bidId, version)
                await connection.execute(query_set, result['name'], result['description'], result['status'], result['employee_username'], bidId)
                result = await UpdateVersion(bidId)
                if result:
                    return result
                return OK
        except Exception as e:
            print(f"BidDAO.RollbackVersion {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)

    async def PatchBidStatus(bidId: UUID, data: PatchRequest):
        connection_pool: asyncpg.Pool = await create_connection_pool()
        try:
            query = "SELECT id FROM bids WHERE id = $1"
            async with connection_pool.acquire() as connection:
                result = await connection.fetch(query, bidId)
                if not result:
                    return BidNotFound
            query = "UPDATE bids SET "
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
            params.append(bidId)

            async with connection_pool.acquire() as connection:
                await connection.execute(query, *params)
                result = await UpdateVersion(bidId)
                if result:
                    return result
                if data.status=="Approved":
                    result_bid = await connection.fetchrow("""SELECT tender_id FROM bids WHERE id=$1""", bidId)
                    print(result_bid['tender_id'])
                    await connection.execute("""UPDATE tenders SET status='Closed' WHERE id=$1""", result_bid['tender_id'])
                return OK
        except Exception as e:
            print(f"BidDAO.PatchBidStatus {e}")
            return InternalError
        finally:
            await close_connection_pool(connection_pool)


async def UpdateVersion(bidId: UUID):
    connection_pool: asyncpg.Pool = await create_connection_pool()
    try:
        query_get = "SELECT id,tender_id,version,name,description,status,version, employee_username, created_at FROM bids WHERE id=$1"
        query_set_bid = "UPDATE bids SET version=$1 WHERE id=$2"
        query_insert_bid_version = """
        INSERT INTO bid_versions(bid_id, tender_id,name, description, status, employee_username, version, created_at)
        VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        """
        async with connection_pool.acquire() as connection:
            result = await connection.fetchrow(query_get, bidId)
            version = result['version']
            version+=1
            await connection.execute(query_set_bid, version, bidId)
            await connection.execute(query_insert_bid_version, 
                                     result['id'], result['tender_id'],result['name'], result['description'],
                                     result['status'], result['employee_username'],
                                     version, result['created_at'])
            
    except Exception as e:
        print(f"BidDAO.UpdateVersion {e}")
        return InternalError
    finally:
        await close_connection_pool(connection_pool)
