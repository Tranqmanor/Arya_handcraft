from fastapi import APIRouter

from app.api.v1.admin import articles, auth, coupons, stats, videos

# 子路由均已带 /admin 前缀,此处不再重复加
admin_router = APIRouter()
admin_router.include_router(auth.router)
admin_router.include_router(videos.router)
admin_router.include_router(articles.router)
admin_router.include_router(coupons.router)
admin_router.include_router(stats.router)