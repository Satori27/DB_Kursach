import asyncio
from datetime import timedelta

from database.conn import DB
from users.auth import create_access_token, get_current_user, hash_password, verify_password, verify_token
from users.dao import UsersDAO
from users.models import UserLogin, UserRegister
from fastapi.middleware.cors import CORSMiddleware


from fastapi import APIRouter, Cookie, Depends, FastAPI, HTTPException, Response
from fastapi import FastAPI, HTTPException

from tenders.router import router as tender_router
from bids.router import router as bid_router
from errors.auth import *


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register")
async def register(user: UserRegister, response: Response):
    # Создаём запись о новом пользователе
    hashed_password = hash_password(user.password)
    result = await UsersDAO.register(user, hashed_password)
    if result is not None:
        raise HTTPException(status_code=401, detail=result)

    # Автоматический вход после регистрации
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return {"message": f"User {user.username} registered successfully"}


@router.post("/login")
async def login(response: Response, user: UserLogin):
    password = await UsersDAO.login(user)
    
    if password==InvalidUser or not verify_password(user.password, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Создание JWT токена
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    
    # Установка токена в куки
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Logged in successfully"}

# Проверка токена из куки

# Пример защищённого эндпоинта
@router.get("/protected")
async def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}!"}

# Выход из системы
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}