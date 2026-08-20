"""初始化数据:写入首篇「毛毡猫咪拍照指南」。

用法(在 server/ 目录下):
  & F:\miniconda3\envs\fastapi\python.exe -m scripts.seed_photo_guide
"""
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Article

GUIDE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "original_resources"
    / "毛毡猫咪拍照指南_润色版.md"
)

TITLE = "定制毛毡猫咪 · 拍照指南 📸"
SUMMARY = "想要一只神似自家猫猫的毛毡猫咪?收藏这份拍照指南,光线、距离、角度一次说清!"
CATEGORY = "photo_guide"
COVER_URL = ""  # 待提供封面图,可留空


def main() -> None:
    if not GUIDE_PATH.exists():
        print(f"[WARN] 未找到润色版文案:{GUIDE_PATH}")
        return

    content = GUIDE_PATH.read_text(encoding="utf-8")

    db = SessionLocal()
    try:
        exists = db.scalar(select(Article).where(Article.title == TITLE))
        if exists:
            print("[SKIP] 已存在同名文章,不重复插入")
            return

        article = Article(
            title=TITLE,
            summary=SUMMARY,
            cover_url=COVER_URL,
            content=content,
            category=CATEGORY,
            is_published=True,
            sort_order=0,
        )
        db.add(article)
        db.commit()
        print(f"[OK] 已插入文章 id={article.id}:{TITLE}")
    finally:
        db.close()


if __name__ == "__main__":
    main()