# cys-prompt-suite

> 中文提示词工程师 + 平台合规校验 一体化 MCP —— **生成即合规**闭环。

把主人的三类中文 AI 提示词技能（写实人像 / 动漫角色 / 海螺3 视频）与一套
**平台合规护栏**合成为一个 MCP 服务：生成提示词后自动过合规校验，命中红线即
自动清洗复检，返回「安全可直接发布」的提示词与自检清单。内置 **8800+ 条**扩展词库（接入
`背景多样性库.md`/`游戏服装多样性库.md`/`国风素材库.md` 等 6 个 md 词表），产出更丰富、更可控。

- 中文优先：提示词本体用中文 9 段式 / 6 段式模板，紧扣国内平台与特定模型（Krea2 / cysdongman / H3）。
- 禁否定词铁律：CFG=1.0 无负向，安全只靠正向约束（长款覆盖 / 领口双清 / 日本8词防切脚）。
- 生成即合规：闭环工具 `generate_and_check` 一次调用完成「生成 → 校验 → 清洗 → 复检」。
- 词库驱动：写实 2646 条（55 分类）+ 动漫 80 家族五维池 + 全局扩展池（8800+ 条），`seed` 可复现。

---

## 1. 安装

```bash
cd cys-prompt-suite
pip install -e .          # 或：uv pip install -e .
```

依赖：`fastmcp>=3.0`（Apache-2.0）。仅一个运行时依赖，零显卡要求（合规校验纯 CPU）。

## 2. 接入 MCP 客户端

stdio 传输，挂到 Claude Desktop / Cursor / Cline 等任意 MCP 客户端：

```json
{
  "mcpServers": {
    "cys-prompt-suite": {
      "command": "python",
      "args": ["-m", "cys_prompt_suite.server"]
    }
  }
}
```

> 本地用托管 Python 时，把 `command` 换成绝对路径，例如
> `"C:/Users/MSI/.workbuddy/binaries/python/envs/default/Scripts/python"`。
>
> 📁 已备好可直接粘贴的配置：见 [`mcp-config/`](./mcp-config/README.md)
> （`claude_desktop_config.json` 合并进 `%APPDATA%\Claude\claude_desktop_config.json`，
> `cursor_mcp.json` 存为项目根 `.cursor/mcp.json`）。

## 3. 工具一览（9 个）

| 工具 | 作用 |
|---|---|
| `generate_portrait_prompt` | 写实人像 9 段式（全身/半身 + 动作迁移硬约束），`use_wordbank` 启用词库 |
| `generate_anime_prompt` | 动漫角色 6 段式（展示/动作迁移双版），按家族从词库采样 |
| `generate_h3_prompt` | 海螺3 视频提示词（T2VA/I2VA/FL2VA/L2VA/Ref2VA，仅舞蹈/转场/展示/走秀） |
| `check_prompt` | 合规扫描：精确短语 + 结构化规则，返回违规项/严重度/建议 |
| `self_check_list` | 发布前自检清单（通用 + 类型专属 + 平台提示） |
| `explain_rule` | 解释某条规则 / 黑名单（如 `BANNED` / `A-LOLI` / `R-PORTRAIT-RIGHT`） |
| `list_platforms` | 抖音/快手/视频号/小红书 四平台审核差异 |
| `list_prompt_options` | 风格/家族/画风/词库分类清单 |
| **`generate_and_check`** | **闭环主工具：生成 → 自动合规校验 → 命中即清洗复检** |

## 4. 闭环用法示例

**Python 直接调用**

```python
from cys_prompt_suite import aggregator

res = aggregator.generate_and_check(
    kind="anime", compliance_type="anime", platform="douyin",
    family="国风仙侠", use_wordbank=True, seed=3,
)
print(res["passed"], res["safe_passed"])   # True True
print(res["prompt"])                        # 可直接喂模型的提示词
print(res["safe_prompt"])                   # 清洗后的安全版本（若有命中）
```

**MCP 客户端调用** `generate_and_check`，返回结构：

```json
{
  "kind": "anime",
  "prompt": "<生成的提示词>",
  "compliance": { "summary": {...}, "violations": [] },
  "passed": true,
  "needs_sanitize": false,
  "sanitized_terms": [],
  "safe_prompt": "<同 prompt>",
  "safe_compliance": { "summary": {...}, "violations": [] },
  "safe_passed": true,
  "self_check": { "checklist": [...] },
  "notes": [...]
}
```

## 5. 词库说明

词库存于 `src/cys_prompt_suite/prompts/data/`：

- `portrait_corpus.json` — 写实 55 分类 / 2646 条（服装形制、国风汉服、鞋履、背景、中国传统色、饰品，新增 风格_全球美学·配色_风格方案·环境_画框感·鞋履_四要素…）
- `anime_lib.json` — 动漫 80 家族（原 14 + 17 服装家族 + 47 游戏家族）五维池 + 全局扩展池（COLORS 中国传统色 + 游戏色板、outfit/bg/acc/shoes/style 大池、47 游戏锚点）

数据由 `scripts/ingest_references.py` 从主人自有技能 `references/`（含 6 个 md 词表）归一化而来，可复现。
生成器默认 `use_wordbank=True`（动漫）/ 可选（写实），按 `seed` 可复现采样。

---

## 6. ⚖️ 可商用确认（Commercial Use）

**结论：本套件可商用（含闭源集成、再分发、商业服务）。**

| 项 | 说明 | 商用结论 |
|---|---|---|
| **本仓库代码** | 原创编写，采用 **MIT License** | ✅ 允许商用、修改、再分发、闭源集成 |
| **运行时依赖** | fastmcp (**Apache-2.0**，含专利授权) / pydantic (**MIT**) / starlette (**BSD-3-Clause**) | ✅ 均为宽松许可，允许商用 |
| **提示词模板** | 源自主人自有技能（迁移01 / 迁移2 / h3-prompt-writing），为主人自有 IP | ✅ 权利人自行开源，可商用 |
| **扩展词库** | 颜色名 / 服饰形制名等**事实性词汇**，源自主人自有技能 references（爬取自百度百科、中国传统色站点等公开事实数据） | ✅ 事实性数据，非版权保护客体，可商用 |
| **第三方版权内容** | 未混入任何受版权保护的创作内容（无歌词、无长段原文、无他人提示词逐字复制） | ✅ 无侵权风险 |

> 免责声明：本工具是「生成辅助 + 合规护栏」，生成结果仍须由使用者按各平台最新规则
> **主动打 AI 标识**并人工终审。合规校验为规则兜底，不替代法律/平台审核。

---

## 7. 组件仓库

本套件已整合以下两个独立组件（如需单独使用亦可）：

- `cys-prompt-mcp` — 仅提示词生成
- `cys-compliance-mcp` — 仅合规校验

`cys-prompt-suite` 将二者 vendored 进 `src/cys_prompt_suite/{prompts,compliance}` 并新增聚合闭环层。

## 8. 许可证

[MIT](./LICENSE) © 2026 chengyansen (cys)
