from fastapi import APIRouter

from app.api.v1 import addresses, articles, arya, auth, carousel, contact, health, orders, uploads, users, videos, works
from app.api.v1.admin.router import admin_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(videos.router)
api_router.include_router(articles.router)
api_router.include_router(contact.router)
api_router.include_router(arya.router)
api_router.include_router(carousel.router)
api_router.include_router(orders.router)
api_router.include_router(addresses.router)
api_router.include_router(uploads.router)
api_router.include_router(works.router)
api_router.include_router(admin_router)
