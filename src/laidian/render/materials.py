"""材质表。

每种材质有一个编号、基础反照率（线性 RGB）和一些光学参数。
程序纹理在 textures.py 里按材质编号批量计算。
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Mat:
    name: str
    albedo: tuple          # 线性 RGB
    gloss: float = 0.0     # 0 = 完全漫反射
    transmit: float = 0.0  # 漫透射比例（床单）
    emissive: tuple = (0.0, 0.0, 0.0)


def srgb(c):
    """sRGB(0-255) -> 线性。"""
    c = np.asarray(c, float) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4))


MATS = [
    Mat("void", (0, 0, 0)),
    Mat("plaster", srgb((226, 220, 204))),          # 刷白的墙，泛黄
    Mat("wainscot", srgb((122, 158, 128))),         # 墙裙绿漆
    Mat("concrete", srgb((128, 124, 116))),         # 水泥地
    Mat("beam", srgb((92, 66, 44))),                # 檩条、椽子
    Mat("roof_tile", srgb((60, 58, 56))),           # 椽子之间露出的青瓦
    Mat("wood_dark", srgb((96, 48, 32)), 0.25),     # 老家具，枣红漆
    Mat("wood_raw", srgb((168, 128, 84))),          # 板凳、本色木
    Mat("bamboo", srgb((204, 178, 112)), 0.15),     # 竹席
    Mat("door_wood", srgb((112, 80, 54))),          # 门板
    Mat("glass", srgb((180, 196, 200)), 0.6, 0.85), # 玻璃
    Mat("screen", srgb((60, 64, 62)), 0.0, 0.55),   # 纱窗
    Mat("metal", srgb((140, 140, 136)), 0.4),       # 吊扇、马灯
    Mat("plastic_white", srgb((228, 224, 214)), 0.2),
    Mat("tv_body", srgb((150, 144, 132)), 0.2),
    Mat("tv_screen", srgb((24, 28, 30)), 0.7),
    Mat("sheet", srgb((236, 232, 222)), 0.0, 0.45), # 棉床单
    Mat("enamel", srgb((232, 230, 222)), 0.5),
    Mat("paper_red", srgb((178, 46, 36))),
    Mat("paper", srgb((222, 212, 186))),
    Mat("stone", srgb((132, 128, 120))),
    Mat("column", srgb((84, 54, 34)), 0.15),
    Mat("wire", srgb((90, 90, 90))),
    Mat("cloth_towel", srgb((196, 120, 110))),
    Mat("cloth_blouse", srgb((150, 170, 196))),
    Mat("cloth_tshirt", srgb((236, 180, 70))),
    Mat("watermelon_red", srgb((210, 60, 60))),
    Mat("watermelon_rind", srgb((70, 120, 60))),
    Mat("soybean", srgb((120, 160, 70))),
    Mat("tube_glass", srgb((240, 244, 246)), 0.3),
    Mat("exterior", srgb((40, 40, 44))),
    Mat("image", (1, 1, 1)),                        # 贴图（画、日历、照片）
    Mat("lamp_glass", srgb((230, 220, 190)), 0.6, 0.8),
    Mat("broom", srgb((176, 150, 96))),
    Mat("thermos", srgb((190, 60, 50)), 0.4),
    Mat("chest", srgb((132, 82, 48)), 0.15),
    Mat("brass", srgb((180, 140, 70)), 0.5),
    # 人物
    Mat("skin_xm", srgb((236, 192, 160))),          # 小满：晒过一点的孩子皮肤
    Mat("skin_nn", srgb((214, 168, 136))),          # 奶奶：更深、偏暖
    Mat("tshirt_xm", srgb((238, 178, 64))),         # 小满的大号 T 恤：橙黄
    Mat("shorts_xm", srgb((62, 104, 150))),         # 小满的短裤：牛仔蓝
    Mat("blouse_nn", srgb((168, 192, 214))),        # 奶奶的碎花短袖：浅蓝底
    Mat("trousers_nn", srgb((48, 50, 62))),         # 奶奶的裤子：藏青黑
    Mat("hair_xm", srgb((30, 26, 24))),
    Mat("hair_nn", srgb((188, 184, 178))),          # 奶奶：灰白
    Mat("shoes_nn", srgb((40, 36, 34))),            # 黑布鞋
    Mat("jade", srgb((120, 176, 140)), 0.5),        # 玉镯
    Mat("sole", srgb((220, 214, 200))),             # 布鞋白底
]
MAT_ID = {m.name: i for i, m in enumerate(MATS)}


def albedo_table():
    return np.array([m.albedo for m in MATS], dtype=np.float64)


def M(name):
    return MAT_ID[name]
