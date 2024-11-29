from fastapi import APIRouter, Depends, HTTPException

from bids.dao import BidDAO

from errors.errors import InternalError
from bids.models import NewRequest, BidStatus, PatchRequest
from users.auth import get_current_user
from uuid import UUID
from errors.bids import BidNotFound

router = APIRouter(prefix='/bids', tags=['Bid'])


@router.get("/{tenderId}")
async def get_bids(tenderId: UUID):

    result = await BidDAO.GetBids(tenderId)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    
    return result

@router.get("/{bidId}/versions")
async def get_tenders(bidId:UUID, user: str = Depends(get_current_user)):
    result = await BidDAO.GetBidVersions(bidId)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.get("/approved/")
async def get_tenders(user: str = Depends(get_current_user)):
    result = await BidDAO.GetBidsApproved(user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.post("/new")
async def new_bid(data: NewRequest, user: str = Depends(get_current_user)):
    result = await BidDAO.NewBid(data,user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)

    return result


@router.get("/my/")
async def get_tenders(user: str = Depends(get_current_user)):
    result = await BidDAO.GetMyBid(user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)

    return result


@router.patch("/{bidId}/edit")
async def patch_bid_status(bidId: UUID, data: PatchRequest, user: str = Depends(get_current_user)):
    result = await BidDAO.PatchBidStatus(bidId, data)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==BidNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result

@router.get("/{bidId}/status")
async def get_bid_status(bidId: UUID, user: str = Depends(get_current_user)):
    result = await BidDAO.GetBidStatus(bidId)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==BidNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result




@router.put("/{bidId}/rollback/{version}")
async def rollback_version(bidId: UUID, version:int, user: str = Depends(get_current_user)):
    result = await BidDAO.RollbackVersion(bidId, version)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==BidNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result

