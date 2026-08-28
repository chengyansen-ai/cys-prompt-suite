# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与
[Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-08-28

### 新增
- 一体化 MCP 服务 `cys-prompt-suite`：中文提示词生成（写实人像 / 动漫角色 / 海螺3 视频）
  + 平台合规校验（抖音 / 快手 / 视频号 / 小红书）合二为一。
- 「生成即合规」闭环工具 `generate_and_check`：生成 → 自动合规校验 → 命中红线自动清洗 → 复检，
  返回可直接发布的安全提示词与自检清单。
- 9 个 MCP 工具：`generate_portrait_prompt` / `generate_anime_prompt` / `generate_h3_prompt` /
  `list_prompt_options` / `check_prompt` / `self_check_list` / `explain_rule` /
  `list_platforms` / `generate_and_check`。
- 扩展词库 **8800+ 条**（写实 55 分类 / 2646 条 + 动漫 80 家族五维池 + 全局扩展池）：
  - 写实：服装形制 / 国风汉服 / 鞋履 / 背景 / 中国传统色 / 饰品，以及 风格_国风签名·全球美学·海外爆款·配色方案·仙侠原型·画框感·鞋履四要素。
  - 动漫：原 14 家族 + 17 服装家族（汉服/旗袍/和服/女仆/机甲/骑士/战术/泳装/晚礼服…）+ 47 游戏家族
    （原神/剑网3/鸣潮/阴阳师…），叠加 游戏锚点 / 服装池 / 背景池 / 饰品池 / 鞋履池 / 风格池 / 游戏色板。
- 数据溯源脚本 `scripts/ingest_references.py`：从主人自有技能 `references/`（6 个 md 词表 + 2 个结构化词库）
  可复现地归一化生成词库 JSON，随仓库开源以证明「事实性词汇、可商用」。
- `seed` 可复现采样；CFG=1.0 无负向提示词（安全只靠正向约束）。
- 红线固化：不做数字人口播/讲课/带货，只产出 舞蹈/转场/展示/走秀 等健康向内容；
  动作迁移版内置 T-pose / 头≤25% / 腿≥65% / 鞋履≥6% / 日本 8 词防切脚硬约束。

### 修复
- `list_prompt_options` 工具运行时 `wordbank` 模块属性引用错误（仅注册时不可见，实机调用时触发）→ 改为直接导入 `wordbank` 子模块。

### 测试
- 5 组测试套件全绿：生成器（含词库采样）/ 合规 / 套件闭环 / 双组件 server 冒烟 / 套件 server 冒烟。
- 新增 `tests/test_full_stdio.py`：官方 `mcp` 客户端对 9 个工具逐一 `tools/call` 往返测试
  （与 Claude Desktop / Cursor 相同连接路径），含「注入违规词 → 自动清洗 → 复检通过」闭环验证。
