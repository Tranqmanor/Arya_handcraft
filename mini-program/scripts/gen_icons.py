"""生成莫兰迪色 tabBar 图标与欢迎页猫爪 logo。

用法:& F:\miniconda3\envs\fastapi\python.exe scripts/gen_icons.py
输出: mini-program/src/static/tab-*.png + logo-paw.png(81×81)
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).resolve().parent.parent / "src" / "static"

SIZE = 81

# 莫兰迪色板
DOVE = (185, 177, 172)    # 未选中  #B9B1AC
PINK = (201, 169, 166)    # 选中    #C9A9A6
CLAY = (169, 139, 132)    # 深主色  #A98B84
CREAM = (250, 246, 240)   # 底色    #FAF6F0


def new_canvas(color):
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, SIZE - 5, SIZE - 5], fill=(*color, 255))
    return img, d


# ---------- 图标绘制函数(均为填充图形,抽象简洁) ----------

def draw_home(d, color):
    """首页:圆角小房子"""
    # 屋顶
    d.polygon([(40, 14), (10, 42), (22, 42), (22, 42), (70, 42), (40, 14)], fill=(*color, 255))
    # 屋身
    d.rounded_rectangle([22, 40, 58, 68], radius=6, fill=(*color, 255))
    # 门(镂空:画底色)
    d.rectangle([36, 50, 46, 68], fill=(255, 255, 255, 0))


def draw_video(d, color):
    """视频:圆角方形 + 播放三角"""
    d.rounded_rectangle([12, 20, 69, 61], radius=12, fill=(*color, 255))
    d.polygon([(31, 32), (31, 52), (52, 42)], fill=(255, 255, 255, 255))


def draw_article(d, color):
    """文章:文档 + 横线"""
    d.rounded_rectangle([22, 12, 59, 69], radius=8, fill=(*color, 255))
    lines = [(29, 26), (52, 26)], [(29, 38), (52, 38)], [(29, 50), (45, 50)]
    for line in lines:
        d.line(line, fill=(255, 255, 255, 255), width=4)


def draw_arya(d, color):
    """Arya:猫爪(一个主垫 + 四颗小垫)"""
    d.ellipse([26, 40, 55, 66], fill=(*color, 255))          # 主垫
    for cx in (17, 30, 42, 55):
        d.ellipse([cx - 7, 22, cx + 7, 38], fill=(*color, 255))  # 四趾


def draw_mine(d, color):
    """我的:人形(头 + 圆肩)"""
    d.ellipse([28, 14, 53, 39], fill=(*color, 255))           # 头
    d.pieslice([10, 36, 71, 88], start=180, end=360, fill=(*color, 255))  # 肩


DRAWERS = {
    "home": draw_home,
    "video": draw_video,
    "article": draw_article,
    "arya": draw_arya,
    "mine": draw_mine,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in DRAWERS.items():
        for suffix, color in (("", DOVE), ("-active", PINK)):
            img, d = new_canvas(color)
            fn(d, color)
            # 选中态不需要额外效果;未选中态把图形压暗一点点以作区分
            if not suffix:
                img = img.convert("RGBA")
            path = OUT_DIR / f"tab-{name}{suffix}.png"
            img.save(path)
            print(f"[OK] {path.name}")

    # 欢迎页猫爪 logo(主垫 + 四趾,粉色系)
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([26, 40, 55, 66], fill=(*PINK, 255))
    for cx in (17, 30, 42, 55):
        d.ellipse([cx - 7, 22, cx + 7, 38], fill=(*CLAY, 255))
    img.save(OUT_DIR / "logo-paw.png")
    print("[OK] logo-paw.png")


if __name__ == "__main__":
    main()