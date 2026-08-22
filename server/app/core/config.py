from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 运行环境
    ENV: str = "dev"

    # CORS 允许来源(逗号分隔,如 https://xxx.pages.dev,https://admin.example.com)
    # ENV=dev 且未配置时放行所有;其他情况未配置则不允许任何跨域来源
    CORS_ORIGINS: str = ""

    # 数据库
    DATABASE_URL: str = "postgresql+psycopg://arya:arya_dev@localhost:5432/arya_handcraft"
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 微信小程序(个人主体)
    WX_APP_ID: str = ""
    WX_APP_SECRET: str = ""

    # 联系店主二维码(留空则前端用自己的 static/wechat-qr.png)
    CONTACT_QR_URL: str = ""

    # 大模型(DeepSeek,OpenAI 兼容)
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "deepseek-v4-flash"

    # 管理后台初始密码
    ADMIN_INIT_PASSWORD: str = ""


    @property
    def cors_origin_list(self) -> list[str]:
        """解析 CORS_ORIGINS 为来源列表。"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
