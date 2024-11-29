import asyncio
from datetime import timedelta

from database.conn import DB
from users.auth import create_access_token, get_current_user, hash_password, verify_password, verify_token
from users.dao import UsersDAO
from users.models import UserLogin, UserRegister
from fastapi.middleware.cors import CORSMiddleware


from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi import FastAPI, HTTPException

from tenders.router import router as tender_router
from bids.router import router as bid_router
from errors.auth import *
from users.router import router as auth_router

# Запуск асинхронной функции
# asyncio.run(DB.init_tables())

app = FastAPI()
app.include_router(tender_router)
app.include_router(bid_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  
    allow_headers=["*"], 
)
