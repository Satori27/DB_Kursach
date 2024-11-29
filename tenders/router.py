from fastapi import APIRouter, Depends, HTTPException

from tenders.dao import TenderDAO

from errors.errors import InternalError
from tenders.models import NewRequest, TenderStatus, PatchRequest
from users.auth import get_current_user
from uuid import UUID
from errors.tender import TenderNotFound

router = APIRouter(prefix='/tenders', tags=['Tender'])




@router.get("/")
async def get_tenders(user: str = Depends(get_current_user)):
    result = await TenderDAO.GetTenders(user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.get("/{tenderId}/versions")
async def get_tenders(tenderId:UUID, user: str = Depends(get_current_user)):
    result = await TenderDAO.GetTenderVersions(tenderId)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result

@router.get("/my/bids")
async def tender_bids(user: str = Depends(get_current_user)):
    result = await TenderDAO.GetTenderBids(user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result



@router.post("/new")
async def new_tender(data: NewRequest, user: str = Depends(get_current_user)):
    result = await TenderDAO.NewTender(data, user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)

    return result


@router.get("/my")
async def my_tender(user: str = Depends(get_current_user)): 
    result = await TenderDAO.GetMyTenders(user)

    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)

    return result

@router.get("/{tenderId}/status")
async def get_tender_status(tenderId: UUID, user: str = Depends(get_current_user)):
    result = await TenderDAO.GetTenderStatus(tenderId)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==TenderNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result

@router.put("/{tenderId}/status")
async def put_tender_status(tenderId: UUID, status: TenderStatus, user: str = Depends(get_current_user)):
    result = await TenderDAO.PutTenderStatus(tenderId, status)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==TenderNotFound:
        raise HTTPException(status_code=400, detail=result)
    return result

@router.patch("/{tenderId}/edit")
async def patch_tender_status(tenderId: UUID, data: PatchRequest, user: str = Depends(get_current_user)):
    result = await TenderDAO.PatchTenderStatus(tenderId, data)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==TenderNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result

@router.put("/{tenderId}/rollback/{version}/")
async def rollback_version(tenderId: UUID, version:int, user: str = Depends(get_current_user)):
    result = await TenderDAO.RollbackVersion(tenderId, version)
    if result==InternalError:
        raise HTTPException(status_code=500, detail=result)
    if result==TenderNotFound:
        raise HTTPException(status_code=400, detail=result)

    return result