# Contributing · 贡献指南

欢迎贡献！本项目是 cys（chengyansen）的开源工作，任何改进都欢迎提 Issue / PR。

## 环境

```bash
# 建议 Python 3.11+；唯一运行时依赖 fastmcp>=3.0
pip install -e .[dev]   # dev: pytest
```

## 目录结构

```
cys-prompt-suite/
├── scripts/ingest_references.py   # 词库归一化（从 skills references/ 生成 data/*.json，可复现）
├── src/cys_prompt_suite/
│   ├── prompts/                   # 三个生成器 + 词库（portrait / anime / h3 / wordbank）
│   ├── compliance/                # 合规规则与扫描（rules / checker）
│   ├── aggregator.py              # 生成即合规 闭环层
│   └── server.py                  # FastMCP server（9 工具）
└── tests/                         # 冒烟 + 闭环 + stdio 往返测试
```

## 词库怎么维护

1. 词库 JSON 由 `scripts/ingest_references.py` 从**事实性词汇源**（颜色名 / 服饰形制名 / 背景名）
   归一化生成，**不要手改** `src/**/data/*.json`。
2. 想扩充词库 → 往 ingest 脚本的候选词表（`OUTFIT_VOCAB` 等）里加词，跑一遍脚本即可，
   解析时会对词源文件做「存在性校验」，保证可溯源。
3. 新增规则 → 在 `compliance/rules.py` 注册，并在 `compliance/checker.py` 暴露。

## 红线（不可妥协）

- CFG=1.0 无负向提示词：新增内容禁止引入否定词写法。
- 内容范围：只做 舞蹈 / 转场 / 展示 / 走秀 等健康向，**不做** 数字人口播 / 讲课 / 带货。
- 合规：发布内容须打 AI 标识；人脸 LoRA 须虚拟形象基底；不做幼态 + 暴露 / 挑逗。

## 提交前

```bash
python tests/test_generators.py
python tests/test_suite.py
python tests/test_server_suite.py
python tests/test_full_stdio.py     # 官方 mcp 客户端 stdio 往返（9 工具全调用）
```

全部 `PASS` 再发 PR。
