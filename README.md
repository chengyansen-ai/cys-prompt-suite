# cys-prompt-suite

把中文人像、动漫角色和 MiniMax H3 视频提示词接入 MCP，并在同一次调用中返回
风险命中、确定性改写结果和人工复核清单。

[![CI](https://github.com/chengyansen-ai/cys-prompt-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/chengyansen-ai/cys-prompt-suite/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](./LICENSE)

> 当前状态：**Beta**。代码和 MCP 接口已有自动化测试；合规模块是启发式文本检查，
> 不是法律意见、平台认证，也不会把生成结果变成“可直接发布”的内容。

## 为什么做这个项目

普通提示词库往往只解决“写什么”，没有解决“参数是否有效、参考帧是否对齐、数据是否
真的随 wheel 发布、结果还需要检查什么”。本项目把这几件事放进一个本地 MCP 服务：

- 生成写实人像 9 段式、动漫角色 6 段式和 H3 五种模式提示词；
- 对无效模式、风格、家族和参数明确报错，不再静默回退；
- 用 `seed` 提供可复现的词库采样；
- 扫描预设风险短语，必要时做确定性替换并再次检查；
- 始终返回 `requires_human_review=true`，保留发布前人工终审；
- 默认隐藏 47 个第三方游戏 IP 家族，只有显式确认后才能启用。

项目本身不调用图像或视频 API，不采集遥测，也不需要 GPU。提示词会经过你的 MCP
客户端和模型提供方，因此仍应按它们的隐私条款处理。

## 能力一览

| 能力 | 输出 | 关键约束 |
|---|---|---|
| 写实人像 | 9 段中文提示词 | 全身/半身、动作迁移构图、可选词库与 LoRA 提示 |
| 动漫角色 | 6 段中文提示词 + 英文质量标签 | 展示/动作迁移、服装风险词清理、第三方 IP 显式授权开关 |
| MiniMax H3 | T2VA / I2VA / FL2VA / L2VA / Ref2VA | 首末帧描述、两位小数时长对齐、Ref2VA 固定六段顺序 |
| 发布前检查 | 结构化命中、建议、复检结果 | NFKC 归一化、去重、规则版本、始终要求人工复核 |
| MCP 接入 | 9 个工具 | FastMCP stdio，可供支持 MCP 的桌面客户端调用 |

## 30 秒开始

需要 Python 3.10 或更高版本。仓库尚未声明已发布到 PyPI，因此从源码安装：

```bash
git clone https://github.com/chengyansen-ai/cys-prompt-suite.git
cd cys-prompt-suite
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

启动 MCP stdio 服务：

```bash
python -m cys_prompt_suite.server
```

客户端配置示例（`python` 必须是安装了本项目的同一个解释器；生产环境建议填绝对路径）：

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

Claude Desktop 和 Cursor 模板见 [`mcp-config/`](./mcp-config/README.md)。

## 最常用的调用

### 生成并检查

```python
from cys_prompt_suite import aggregator

result = aggregator.generate_and_check(
    kind="anime",
    family="国风仙侠",
    use_wordbank=True,
    seed=3,
)

print(result["safe_prompt"])
print(result["safe_passed"])            # 仅代表启发式规则复检结果
print(result["requires_human_review"])  # 始终为 True
print(result["ruleset"])
```

如果传错参数名，调用会抛出 `ValueError`，不会像早期版本那样悄悄忽略。

### H3 首末帧对齐

```python
from cys_prompt_suite.prompts.h3 import generate_h3_prompt

result = generate_h3_prompt(
    mode="FL2VA",
    duration_seconds=8,
    first_frame_desc="a closed umbrella beside a bicycle",
    last_frame_desc="the same umbrella open above the cyclist",
    integrated_multimodal_description="She opens it in one continuous shot.",
)
print(result["prompt"])
```

`FL2VA` 和 `L2VA` 必须提供正数 `duration_seconds`，输出使用 `8.00-second mark`
这样的两位小数对齐格式。

## 9 个 MCP 工具

| 工具 | 作用 |
|---|---|
| `generate_portrait_prompt` | 生成写实人像 9 段式提示词 |
| `generate_anime_prompt` | 生成动漫角色 6 段式提示词 |
| `generate_h3_prompt` | 生成五种 H3 模式提示词 |
| `generate_and_check` | 生成、扫描、按命中词改写并复检 |
| `check_prompt` | 扫描已有提示词或文案 |
| `self_check_list` | 返回通用、内容类型和渠道复核项 |
| `explain_rule` | 查询指定启发式规则 |
| `list_platforms` | 返回支持的渠道名称和 AI 标识提醒 |
| `list_prompt_options` | 返回可用风格、家族、模式和词库统计 |

## 词库：把“累计条目”和“唯一词量”说清楚

随 wheel 一起发布的两个 JSON 快照共有：

- 写实词库：55 个列表分类，2,646 个索引条目；
- 动漫词库：80 个家族和多个全局池，其中 47 个是第三方游戏 IP 锚点；
- 合计：**8,865 个索引条目，3,455 个唯一字符串**。

“索引条目”会重复计算同一字符串在多个家族或分类中的出现，不能等同于 8,865 个独立词。
可用 `get_wordbank_stats()` 在运行时复核。数据来源限制和新增数据要求见
[`docs/DATA_PROVENANCE.md`](./docs/DATA_PROVENANCE.md)。

第三方游戏 IP 家族不会出现在默认列表中。确有授权或其他合法依据时，调用方才能显式启用：

```python
generate_anime_prompt(
    family="原神",
    allow_third_party_ip=True,
)
```

这个开关只防止误用，不提供任何版权、商标、角色形象或商品化权授权。

## “合规检查”到底保证什么

检查器会做 Unicode NFKC 归一化、精确短语匹配、规则去重、确定性替换和复检。返回的
`safe_passed=true` 只表示当前规则集没有再次命中配置短语。它无法识别全部语境、画面、
音频、广告陈述、授权状态或平台实时政策。

商用前请阅读 [`docs/COMMERCIAL_USE.md`](./docs/COMMERCIAL_USE.md)，至少人工检查：

- 人脸、角色、商标、音乐、字体和参考素材是否有权使用；
- 下游模型、API 和素材库是否允许你的商业场景；
- 输出画面和文案是否满足目标地区法律与平台最新规则；
- 是否按要求添加显式或隐式 AI 内容标识。

本仓库的 MIT 许可证允许商业使用**代码**，不等于对数据、输入、模型或输出作全面权利清除。

## 开发与验证

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest -q
python -m build
```

测试覆盖参数校验、确定性采样、IP 默认隔离、H3 对齐、合规改写、9 个 MCP 工具的
内存调用、真实 stdio 往返和包资源读取。CI 在 Python 3.10、3.11、3.12 上运行，并检查
构建出的 wheel 是否包含两个 JSON 词库。

```text
src/cys_prompt_suite/          Python 包与 MCP 服务
├── prompts/                   三类生成器与词库
├── compliance/                可版本化的启发式规则
├── aggregator.py              生成、扫描、改写、复检
└── server.py                  9 个 FastMCP 工具
tests/                         pytest 与 stdio 回归测试
docs/                          质量、数据来源与商用边界
```

贡献方法见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)，漏洞报告见 [`SECURITY.md`](./SECURITY.md)。

## License

代码采用 [MIT License](./LICENSE)。第三方名称、用户输入、下游模型和生成内容的权利需
分别评估。
