# -*- coding: utf-8 -*-
"""
wordbank.py — 扩展词库加载与采样层

数据来自 data/portrait_corpus.json（写实 55 类 / 2646 条）与 data/anime_lib.json
（动漫 80 家族(原14+17服装+47游戏)五维池 + 全局池 / 8800+ 条），由
scripts/ingest_references.py 从主人自有技能 references/（含 6 个 md 词表）归一化而来。
本层只做「加载 + 可复现随机采样」，不引入新规则。

所有采样接受 seed 参数，保证测试与复现可重现。
"""
import json
import os
import random

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    with open(os.path.join(_HERE, "data", name), "r", encoding="utf-8") as f:
        return json.load(f)


_PORTRAIT = _load("portrait_corpus.json")
_ANIME = _load("anime_lib.json")


# ============================================================================
# 写实人像词库
# ============================================================================

def get_portrait_categories() -> list:
    """返回所有可用的写实词库分类名（如 服装_国风形制 / 鞋履_国风 / 背景 / 色彩_红色系 / 风格_全球美学）。"""
    return [k for k in _PORTRAIT
            if k not in ("_meta", "_meta_new", "总词汇量") and isinstance(_PORTRAIT.get(k), list)]


def sample_portrait(category: str, n: int = 1, seed: int | None = None) -> list:
    """从某写实分类随机抽取 n 条（不重复）。分类不存在返回 []。"""
    items = _PORTRAIT.get(category)
    if not isinstance(items, list) or not items:
        return []
    rng = random.Random(seed)
    n = min(n, len(items))
    return rng.sample(items, n)


def sample_portrait_color(seed: int | None = None) -> str | None:
    """随机抽一个颜色（从 色彩_* 分类里随机选一类再抽一色）。"""
    color_cats = [k for k in _PORTRAIT if k.startswith("色彩_") and isinstance(_PORTRAIT[k], list) and _PORTRAIT[k]]
    if not color_cats:
        return None
    rng = random.Random(seed)
    cat = rng.choice(color_cats)
    return rng.choice(_PORTRAIT[cat])


# ============================================================================
# 动漫角色词库
# ============================================================================

def list_anime_families() -> list:
    """返回动漫词库中所有家族名（原14 + 17服装家族 + 47游戏家族）。"""
    return list(_ANIME["families"].keys())


def get_anime_family(family: str) -> dict | None:
    """返回某家族的五维池 {bg, outfit, style, acc, shoes}，不存在返回 None。"""
    return _ANIME["families"].get(family)


def sample_anime(family: str, dim: str, n: int = 1, seed: int | None = None) -> list:
    """从某家族某维度（bg/outfit/style/acc/shoes）随机抽取 n 条。"""
    fam = _ANIME["families"].get(family)
    if not fam:
        return []
    items = fam.get(dim, [])
    if not items:
        return []
    rng = random.Random(seed)
    n = min(n, len(items))
    return rng.sample(items, n)


def get_anime_colors() -> list:
    return list(_ANIME["colors"])


def sample_anime_colors(n: int = 1, seed: int | None = None) -> list:
    cols = _ANIME["colors"]
    if not cols:
        return []
    rng = random.Random(seed)
    n = min(n, len(cols))
    return rng.sample(cols, n)


# ============================================================================
# 动漫全局扩展池（md 词表聚合池）
# ============================================================================

_GLOBAL_DIM_KEY = {
    "outfit": "outfit_pool", "bg": "bg_pool", "acc": "acc_pool",
    "shoes": "shoes_pool", "style": "style_pool",
}


def sample_anime_global(dim: str, n: int = 1, seed: int | None = None) -> list:
    """从全局扩展池（outfit/bg/acc/shoes/style）随机抽取 n 条（跨家族更丰富）。"""
    key = _GLOBAL_DIM_KEY.get(dim)
    items = _ANIME.get(key, []) if key else []
    if not items:
        return []
    rng = random.Random(seed)
    n = min(n, len(items))
    return rng.sample(items, n)


def sample_color_palettes(n: int = 1, seed: int | None = None) -> list:
    """从游戏色板聚合池随机抽取 n 条配色 token。"""
    items = _ANIME.get("color_palettes", [])
    if not items:
        return []
    rng = random.Random(seed)
    n = min(n, len(items))
    return rng.sample(items, n)


def sample_game_anchor(seed: int | None = None) -> str | None:
    """随机抽一个游戏原型锚点（如 原神/剑网3/鸣潮/阴阳师）。"""
    items = _ANIME.get("game_anchors", [])
    if not items:
        return None
    return random.Random(seed).choice(items)


# 兼容层：把组件里用到的旧 FAMILIES 维度名映射出来（anime.py 也可直接 import 本层）
ANIME_LIB_FAMILIES = _ANIME["families"]
ANIME_LIB_COLORS = _ANIME["colors"]

