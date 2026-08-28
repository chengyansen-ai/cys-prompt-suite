# -*- coding: utf-8 -*-
"""
prompts_data.py — 中文提示词工程师 MCP 的数据层

萃取自主人本地技能（迁移01 / 迁移2 / h3-prompt-writing）的「可复用模板与约束」。
这是生成器的知识源，所有技能红线（禁否定词 / CFG=1 无负向 / 头身比 / 鞋履入镜 /
动作迁移硬约束 / H3 六段式）均在此固化，生成器只做参数化装配，不引入新规则。

注意：本文件只萃取「结构 + 内核段 + 硬约束」，未搬运技能里 1000+ 条的扩展词库
（real-portrait-corpus / anime_big_lib / style-presets）。需要更丰富的服装/鞋履/背景
词池时，可把技能 references/ 下的词库直接接入本文件的 STYLE_PRESETS / WORD_BANK。
"""

# ============================================================================
# 迁移01 · 写实人像 9 段式内核（跨图高度复用的「真实感内核」）
# ============================================================================

# 段2 面容 —— 两个版本：完整版 / 精简版（头身比修正时优先用精简版）
PORTRAIT_FACE_FULL = (
    "年轻清透的亚洲女孩面容，皮肤白皙透亮呈现自然水光感，素颜或淡妆皆可的通透好肤质，"
    "毛孔细腻肤色均匀，双颊带着健康的自然红润，清澈的圆眼睛明亮有神，睫毛自然纤长微翘，"
    "鼻子小巧挺拔，嘴唇淡粉饱满水润，流畅的瓜子脸或鹅蛋脸轮廓，骨相清秀端正，"
    "带着20岁女孩特有的青春气息，笑容自然甜美不做作，眼神清澈有活力"
)
PORTRAIT_FACE_LITE = (
    "东方辨识度的精致五官，皮肤白透粉，水光肌质感，素颜感通透润泽，毛孔细腻，健康血色，"
    "圆眼清澈有神，睫毛纤长自然上翘，鼻子小巧挺拔，唇色淡粉饱满，瓜子脸轮廓流畅，骨相端正，"
    "眼角微挑，眼神平视镜头，清纯自然气质"
)

# 段3 妆容
PORTRAIT_MAKEUP = (
    "清透自然的年轻妆容，淡雅眼妆突出明亮的眼神，自然眉形不过度修饰，睫毛轻翘不厚重，"
    "水润淡粉或裸色唇妆，清透底妆呈现自然好肤质，双颊带着若有若无的淡粉腮红，"
    "整体妆容干净清新，突出20岁女孩的天然好气色"
)

# 段4 身材
PORTRAIT_BODY = (
    "青春活力的年轻女性身材，体态匀称自然，纤细的腰身，修长笔直的双腿，精致锁骨清晰可见，"
    "肩线优美平直，腹部平坦紧致，四肢纤细修长，身材比例自然协调，肌肤白皙透亮，"
    "充满20岁女孩特有的青春朝气与活力，真实自然的年轻体态"
)

# 段5 装饰（黑长直发基底，可按需改发色/首饰）
PORTRAIT_DECOR = (
    "黑色长直发如瀑布般披散在肩上，发质柔顺有光泽如同黑色丝绸，"
    "几缕发丝自然垂落在胸前若隐若现地遮挡着饱满胸部，{jewelry}，美甲整洁美观涂着淡粉色甲油，"
    "脚踝处可系细链装饰，整体装饰提升时尚感和精致度，每个细节都散发致命吸引力"
)
PORTRAIT_JEWELRY_DEFAULT = (
    "简约精致的珠宝配饰，细链条项链垂落在锁骨间，小巧耳钉，精致手链"
)

# 段6 动作 —— 三种范式
PORTRAIT_POSE_MIGRATION = (
    "身体笔直垂直站立面向镜头呈标准采集姿态，双脚并拢呈立正姿态重心均匀分布于双脚，"
    "双手自然下垂贴于身体两侧手指放松舒展，全身从头顶到脚底完整呈现垂直站立的T-pose采集姿态，"
    "头部正直面部正对镜头下巴微收，双肩放松下沉自然水平，腰部挺直脊柱笔直不弯曲，"
    "双膝并拢伸直不弯曲，脚踝并拢，全身S型曲线在垂直站立姿态下完美展现，"
    "表情自然带着若有若无的浅笑，眼神直视镜头充满自信，"
    "脚穿{shoes}清晰完整地展示在画面最底部方便AI采集全身包括鞋子的完整数据"
)
PORTRAIT_POSE_FREE = (
    "身体笔直站立面向镜头重心落于一条腿姿态挺拔自信展现全身S型曲线，"
    "一只手轻轻撩起发丝另一只手自然垂落身侧手指放松修长，嘴角带着若有若无的妩媚笑意眼神直视镜头，"
    "身体微微前倾凸显丰满胸部，腰肢微扭展现完美臀线，双脚并拢脚穿{shoes}优雅站立"
)
PORTRAIT_POSE_HALFBODY = (
    "身体正面直立面向镜头重心居中，双肩放松下沉呈自然水平，"
    "双手自然摆放于身侧或轻搭胸前手指修长放松，表情自然带着微笑，眼神直视镜头"
)

# 段9 摄像 —— 迁移范式 / 上半身范式 / 自由华丽范式
PORTRAIT_CAM_MIGRATION = (
    "Full body standing pose capture（全身垂直站立姿态采集），正面平视机位与人物平齐，"
    "全身垂直构图从头顶到脚底完整入镜绝不裁切，画面底部必须完整包含鞋子且鞋子清晰可见占比不小于画面高度6%，"
    "头部面部占比严格不超过画面总高度的25%，从腰线到脚底的腿部区域必须占据画面人物高度的65%以上"
    "下半身是视觉主体而非面部，全身等比无畸变无透视压缩，8K超高清画质，RAW格式原片，"
    "焦点对准全身确保从头到脚全部清晰锐利尤其开衩处腿部线条和鞋履细节清晰可辨，"
    "景深适中确保人物全身清晰而背景适度虚化，完美还原肌肤质感和服装每一处细节，"
    "色彩科学精准肤色白皙透粉自然，构图完美居中，人物在画面中占据约90%高度且下半身腿部区域占比大于上半身，"
    "顶部留白适中底部必须完整保留鞋子可见，无AI痕迹，专业动作采集摄影质感如同动作迁移采集棚的标准全身扫描图"
)
PORTRAIT_CAM_HALFBODY = (
    "上半身中景构图，85mm镜头取景至腰部以上，正面平视机位与人物胸部平齐，"
    "画面包含头颈肩臂以及腰部以上区域（不裁切双手），头部面部占比≤40%，"
    "背景适度虚化突出人物主体，电影感打光，8K高清，真实摄影质感"
)
PORTRAIT_CAM_FREE = (
    "{light}（{light_en}），{quality}，8K超高清{style}大片质感，焦点清晰锐利，"
    "色彩以{color}为主{atmosphere}，整体氛围{mood}"
)

# ============================================================================
# 迁移2 · 动漫角色 6 段式内核
# ============================================================================

# 段2 画风签名预设（来源于爬取的全球指南 + Danbooru）
ANIME_ART_STYLES = {
    "cel_shading": "anime coloring, cel shading, flat colors, clean lineart, toony",
    "thick_painting": "thick painting style, impasto, oil painting texture, painterly",
    "watercolor": "watercolor style, soft edges, transparent washes",
    "3d_cg": "3D CG rendering, PBR textures, subsurface scattering, Unreal Engine 5",
    "ink_wash": "ink wash style, sumi-e, water and ink, ethnic elements",
    "ghibli": "Ghibli style, soft outlines, warm palette, Studio Ghibli",
    "comic": "thick lineart, bold outlines, cartoon, comic style",
    "airbrush": "anime key visual style, airbrushed shading, gradient shading",
}

# 头部特征固化（部分家族必带，来源于技能「家族体系」）
ANIME_FAMILIES = {
    "国风仙侠": {"quota": 25, "head": "", "note": "汉服/仙侠长款"},
    "国漫漫剧风": {"quota": 20, "head": "", "note": "中国二次元古风美型"},
    "东方龙女": {"quota": 12, "head": "龙角必带·青玉/玄冥色系", "note": "龙角/龙尾"},
    "敦煌飞天": {"quota": 12, "head": "", "note": "飘带飞天"},
    "现代都市": {"quota": 8, "head": "", "note": "校园/都市"},
    "赛博朋克": {"quota": 4, "head": "", "note": "霓虹机能"},
    "九尾狐妖": {"quota": 6, "head": "狐耳必带", "note": "青丘"},
    "武侠剑修": {"quota": 5, "head": "斗笠/长剑必带", "note": "青山松风"},
    "朱雀神女": {"quota": 4, "head": "凤冠/凰羽发簪必带", "note": "赤金星坛"},
    "暗黑魔女": {"quota": 2, "head": "魔角/暗月发冠必带", "note": "中国暗黑仙侠"},
    "花仙精灵": {"quota": 2, "head": "花冠/花神发簪必带", "note": "花神"},
}

# 动漫动作迁移「日本8词」防切脚（tbs283blog 验证最优全身配方）
ANIME_JP8 = [
    "standing", "full-body shot", "feet fully visible", "no cropping at the feet",
    "shoes clearly shown", "visible ground below the feet",
    "feet not touching bottom edge", "shot with room to breathe",
]

# 动漫质量头（路线A/B 通用）
ANIME_QUALITY_HEAD = "(masterpiece:1.2), (best quality:1.2), high resolution, ultra-detailed, professional, intricate details, sharp focus"

# 默认固定人设（人物迁移同脸，来源于生成器写死项）
ANIME_DEFAULT_FACE = "瓜子脸大圆眼，漆黑长直发，极白透粉肌肤，沙漏身材"

# ============================================================================
# H3（海螺3 / MiniMax）视频提示词结构常量
# ============================================================================

H3_BASE_FIELDS = ["integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]
H3_REF_FIELDS = [
    "subject_definitions", "summary", "retention_analysis",
    "detailed_description", "overall_soundscape", "non_diegetic_music",
]

# 健康向内容类型（范围红线：不做口播/讲解/讲课，只舞蹈/转场/展示/走秀）
H3_CONTENT_TYPES = {
    "dance": "健康向国风舞：双臂舒展、水袖/裙摆随旋转飞扬、以腰为轴的舒缓回旋、步态轻盈",
    "transition": "在舞蹈流动中做场景/服饰/光线渐变，转场如舞步连贯顺滑、无跳切",
    "showcase": "匀速行进、定点转身、衣摆拖尾，镜头小幅环绕",
    "catwalk": "走秀：匀速行进、定点转身、衣摆拖尾",
}

# ============================================================================
# 风格预设（可直接套用的 服装/环境/配色签名）
# 形式上 {scene, top, bottom, shoes, colors, light, light_en, atmosphere, mood}
# 仅示例级，覆盖主人常用场景；完整词库见技能 references/style-presets.md
# ============================================================================

STYLE_PRESETS = {
    "唐风": {
        "scene": "大唐盛世牡丹园，层层叠叠的牡丹在午后阳光下娇艳欲滴，汉白玉栏杆蜿蜒，"
                 "远处大明宫飞檐在暖光中金碧辉煌，空气中浮动的落蕊与暖光尘埃",
        "colors": "牡丹粉、汉白玉白与琉璃金", "style": "大唐华贵",
        "light": "午后暖光", "light_en": "warm afternoon light",
        "atmosphere": "华贵暖调", "mood": "盛世雍容",
        "bottom": "齐胸襦裙高腰及踝，胭脂红长裙自胸前高腰线垂坠及踝，裙摆微A字占据画面4/5，"
                  "行走间小腿若隐若现优雅得体；内层配胭脂红安全衬裤完整包裹防走光但不外露",
        "top": "上半身：月白真丝大袖对襟衫敞开飘逸，对襟边缘绣金线牡丹纹，宽袖及地流动如云，"
               "内搭同色系抹胸严密裹胸",
        "shoes": "胭脂红云头锦履，平底，鞋面胭脂红织锦盘金绣凤穿牡丹纹，鞋口滚金边",
    },
    "月夜欧式": {
        "scene": "月夜欧式露台，雕花石栏环绕，远处城市灯火与河面倒影，夜空星河低垂，"
                 "微凉夜风拂动纱幔，空气中悬浮的细碎光尘",
        "colors": "月银、雾蓝与暖金", "style": "欧式浪漫",
        "light": "冷月侧光", "light_en": "cool moonlight from the side",
        "atmosphere": "静谧清冷", "mood": "优雅神秘",
        "bottom": "垂坠感长裙及踝，深蓝丝缎裙摆随夜风轻扬，下摆暗纹刺绣",
        "top": "银线刺绣的露肩晚装上衣，外搭轻透纱披肩",
        "shoes": "银色细高跟鞋，尖头，漆面光泽，细链踝带",
    },
    "现代都市": {
        "scene": "现代都市黄昏天台，玻璃幕墙折射暖橘夕照，远处车流光轨，城市天际线，"
                 "空气中漂浮的暖色尘埃与微风",
        "colors": "暖橘、雾霾蓝与水泥灰", "style": "都市时尚",
        "light": "黄昏逆光", "light_en": "golden-hour backlight",
        "atmosphere": "都市活力", "mood": "自信飒爽",
        "bottom": "高腰阔腿西装裤，垂感挺括，裤脚微喇",
        "top": "廓形西装外套内搭基础针织，利落剪裁",
        "shoes": "裸色尖头高跟鞋，裸粉漆面，细跟",
    },
    "国风仙侠": {
        "scene": "仙山云海，层云如浪翻涌于脚下，远处琼楼玉宇在霞光中若隐若现，"
                 "灵鸟掠过留下流光尾迹，空气中飘散的灵气光粒",
        "colors": "青碧、月白与流金", "style": "仙侠缥缈",
        "light": "晨曦丁达尔光", "light_en": "dawn godrays",
        "atmosphere": "空灵仙气", "mood": "清冷出尘",
        "bottom": "飘逸长裙及地，月白轻纱外层随灵气流动，内衬青碧绣纹长裙",
        "top": "广袖长袍对襟，银线云纹，外披半透明月白纱衣",
        "shoes": "云头锦履，平底，鞋面青碧绣云纹，金线滚边",
    },
}

# 鞋履四要素模板（段7 必写：色 + 材质 + 款型 + 细部）
SHOES_TEMPLATE = "{color}{material}{style}，{detail}，清晰完整地展示在画面最底部"

# 默认绚丽环境前景/中景/天空/微粒占位（段8 画框感）
ENV_FRAME_DEFAULT = "前景虚化物形成画框感"
ENV_MID_DEFAULT = "中景主体清晰"
ENV_SKY_DEFAULT = "天空光效柔和"
ENV_PARTICLES_DEFAULT = "空气中浮动的微光尘埃"
