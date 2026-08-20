from fastapi import APIRouter

from app.api.v1 import articles, arya, auth, contact, health, users, videos
from app.api.v1.admin.router import admin_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(videos.router)
api_router.include_router(articles.router)
api_router.include_router(contact.router)
api_router.include_router(arya.router)
api_router.include_router(admin_router)
