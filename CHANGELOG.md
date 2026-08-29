# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与
[Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2026-08-29

### Added

- 27 条 pytest 回归测试，覆盖生成器、H3、合规、内存 MCP、stdio 与包资源。
- Python 3.10–3.12 CI、Ruff 和构建后 wheel 数据文件检查。
- 数据来源、商用边界、隐私和安全说明。
- `get_wordbank_stats()`，明确索引条目与唯一字符串的统计口径。

### Changed

- 所有公开枚举参数改为严格校验；未知参数不再被聚合器静默丢弃。
- FL2VA/L2VA 使用显式 `duration_seconds` 生成两位小数的参考帧时间对齐。
- 默认动漫家族列表排除 47 个第三方游戏 IP 家族；启用时必须显式确认。
- 合规报告包含规则版本和 `requires_human_review=true`，不再宣称结果可直接发布。
- 默认人像与动漫文案改为更中性、成年且不聚焦性征的表达。
- 运行时依赖约束为 `fastmcp>=3.4,<4`。

### Fixed

- wheel 现在包含两个 JSON 词库。
- Unicode 全角字符可被 NFKC 归一化后检查。
- 重复规则命中与重复清洗词被合并；删除式清洗改为确定性健康表达替换。
- 自定义动漫服装全部被过滤时，不再生成空的 `服装：，` 段落。
- 修复写实相机约束中缺失的中文标点。

## [0.1.0] - 2026-08-28

### Added

- 首个公开版本：三类提示词生成器、启发式发布前检查、9 个 MCP 工具与两个 JSON 词库快照。
