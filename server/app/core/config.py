from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 运行环境
    ENV: str = "dev"

    # 数据库
    DATABASE_URL: str = ""
    REDIS_URL: str = ""

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
    LLM_MODEL: str = "deepseek-chat"

    # 管理后台初始密码
    ADMIN_INIT_PASSWORD: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
