from datetime import timedelta

from users.auth import create_access_token, get_current_user, hash_password, verify_password
from users.dao import UsersDAO
from users.models import UserLogin, UserRegister


from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import HTTPException

from errors.auth import *
from errors.errors import InternalError

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register")
async def register(user: UserRegister, response: Response):

    hashed_password = hash_password(user.password)
    result = await UsersDAO.register(user, hashed_password)
    if result is not None:
        raise HTTPException(status_code=401, detail=result)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"message": f"User {user.username} registered successfully"}


@router.get("/user")
async def get_user(user: str = Depends(get_current_user)):
    result = await UsersDAO.get_user(user)
    if result == InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.get("/organizations")
async def get_org():
    result = await UsersDAO.get_organizations()
    if result == InternalError:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.post("/login")
async def login(response: Response, user: UserLogin):
    password = await UsersDAO.login(user)

    if password == InvalidUser or not verify_password(user.password, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30))

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Logged in successfully"}


@router.get("/protected")
async def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}!"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
