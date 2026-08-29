# Contributing

欢迎提交可验证的小改动。行为变化应先写回归测试，再修改实现。

## 本地环境

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 提交前检查

```bash
python -m ruff check .
python -m pytest -q
python -m build
```

新增或修改 MCP 工具时，同时更新内存调用和 stdio 往返测试。修改打包配置时，检查 wheel
中存在 `portrait_corpus.json` 与 `anime_lib.json`。

## 数据和规则变更

- 词库贡献必须按 [`docs/DATA_PROVENANCE.md`](./docs/DATA_PROVENANCE.md) 记录来源、日期、
  许可/条款、转换方法、权利风险和计数变化。
- 不要提交私人词库、个人数据、未授权的人脸、抓取的创作性长文本或密钥。
- 新增合规规则必须附正例、反例和规范来源日期。
- 不要把启发式命中写成法律结论或平台放行保证。
- 第三方品牌或角色家族必须保持默认关闭，并有明确的显式启用路径。

## Pull request

说明问题、设计选择、测试证据和兼容性影响。公共参数或返回结构变化应更新 README、
CHANGELOG 和相应测试。安全问题请按 [`SECURITY.md`](./SECURITY.md) 私下报告。
