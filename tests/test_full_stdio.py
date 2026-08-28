# -*- coding: utf-8 -*-
"""cys-prompt-suite 全工具 stdio 往返测试（官方 mcp 客户端，与 Claude Desktop 同路径）。

用法：python -u tests/test_full_stdio.py
"""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PY = "C:/Users/MSI/.workbuddy/binaries/python/envs/default/Scripts/python.exe"


def _text(res) -> str:
    txt = ""
    for c in res.content:
        if getattr(c, "type", "") == "text":
            txt += c.text
    return txt


async def run() -> bool:
    params = StdioServerParameters(command=PY, args=["-m", "cys_prompt_suite.server"])
    results = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            results.append(("tools/list", True, "9 tools" if len(names) == 9 else f"{len(names)} tools"))

            async def invoke(name, args):
                r = await session.call_tool(name, args)
                try:
                    return json.loads(_text(r))
                except Exception:
                    return {"raw": _text(r)[:200]}

            d = await invoke("generate_portrait_prompt",
                             {"composition": "full_body", "motion_migration": True,
                              "style": "唐风", "use_wordbank": True, "seed": 7})
            results.append(("generate_portrait_prompt",
                            isinstance(d, dict) and "prompt" in d and "25%" in d["prompt"] and "T-pose" in d["prompt"], ""))

            d = await invoke("generate_anime_prompt",
                             {"family": "原神", "mode": "motion_migration",
                              "use_wordbank": True, "seed": 7})
            results.append(("generate_anime_prompt",
                            isinstance(d, dict) and "prompt" in d and "standing, full-body shot" in d["prompt"], ""))

            d = await invoke("generate_h3_prompt", {"mode": "Ref2VA", "content_type": "dance"})
            h3_ok = isinstance(d, dict) and "prompt" in d and "Ref2VA" in str(d.get("mode", ""))
            results.append(("generate_h3_prompt", h3_ok, f"mode={d.get('mode') if isinstance(d, dict) else d}"))

            d = await invoke("list_prompt_options", {})
            n_fam = len(d.get("wordbank_anime_families", [])) if isinstance(d, dict) else -1
            n_cat = len(d.get("wordbank_portrait_categories", [])) if isinstance(d, dict) else -1
            results.append(("list_prompt_options",
                            isinstance(d, dict) and n_fam >= 80 and n_cat >= 55,
                            f"anime_families={n_fam}, portrait_categories={n_cat}"))

            r = await session.call_tool("check_prompt",
                                        {"prompt": "一位年轻女性，长裙覆盖端庄，全身入镜，鞋履完整",
                                         "content_type": "real", "platform": "douyin"})
            raw = _text(r)
            d = None
            try:
                d = json.loads(raw)
            except Exception:
                pass
            results.append(("check_prompt",
                            isinstance(d, dict) and "summary" in d and d["summary"].get("passed") is True,
                            raw[:160]))

            d = await invoke("self_check_list", {"content_type": "anime", "platform": "douyin"})
            results.append(("self_check_list", isinstance(d, dict), ""))

            d = await invoke("explain_rule", {"rule_id": "BANNED"})
            results.append(("explain_rule", isinstance(d, dict) and not d.get("error"), ""))

            d = await invoke("list_platforms", {})
            results.append(("list_platforms", isinstance(d, dict), ""))

            d = await invoke("generate_and_check",
                             {"kind": "anime", "platform": "douyin",
                              "family": "敦煌飞天", "use_wordbank": True, "seed": 5})
            results.append(("generate_and_check(clean)",
                            isinstance(d, dict) and d.get("passed") is True and d.get("safe_passed") is True, ""))

            d = await invoke("generate_and_check",
                             {"kind": "portrait", "platform": "douyin",
                              "character": "扭臀挑逗顶胯的少女", "use_wordbank": True, "seed": 5})
            ok = (isinstance(d, dict) and d.get("needs_sanitize") is True
                  and d.get("safe_passed") is True and len(d.get("sanitized_terms", [])) > 0)
            info = (f"needs_sanitize={d.get('needs_sanitize')}, safe_passed={d.get('safe_passed')}, "
                    f"cleaned={d.get('sanitized_terms')}") if isinstance(d, dict) else "bad result"
            results.append(("generate_and_check(inject)", ok, info))

    print("\n=== cys-prompt-suite 全工具 stdio 往返测试 ===")
    allok = True
    for name, ok, info in results:
        if not ok:
            allok = False
        tail = ("  " + info) if info else ""
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, tail))
    print("\n总结: " + ("全部合格" if allok else "存在失败"))
    return allok


if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
