# -*- coding: utf-8 -*-
"""cys-prompt-suite server 冒烟测试（FastMCP 内存客户端，验证工具注册与传输）。"""
import sys, os, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastmcp import Client
from cys_prompt_suite import server


async def main():
    async with Client(server.mcp) as client:
        tools = await client.list_tools()
        names = sorted(t.name for t in tools)
        print("注册工具:", names)
        assert "generate_and_check" in names
        assert "generate_portrait_prompt" in names
        assert "generate_anime_prompt" in names
        assert "generate_h3_prompt" in names
        assert "check_prompt" in names

        # 实调闭环工具
        res = await client.call_tool("generate_and_check", {
            "kind": "anime", "compliance_type": "anime", "platform": "douyin",
            "family": "国风仙侠", "use_wordbank": True, "seed": 3,
        })
        data = res.data
        print("generate_and_check.passed =", data["passed"])
        print("generate_and_check.safe_passed =", data["safe_passed"])
        assert data["passed"] is True
        assert data["safe_passed"] is True

        # 实调纯生成工具
        res2 = await client.call_tool("generate_portrait_prompt", {
            "composition": "full_body", "use_wordbank": True, "seed": 3,
        })
        assert res2.data["prompt"]
        print("generate_portrait_prompt 返回长度:", len(res2.data["prompt"]))

        # 实调合规校验
        res3 = await client.call_tool("check_prompt", {
            "prompt": "国风长裙少女健康向古风舞，全身入镜鞋履完整", "content_type": "anime",
        })
        print("check_prompt.passed =", res3.data["summary"]["passed"])
        assert res3.data["summary"]["passed"] is True

    print("\n✅ cys-prompt-suite server 冒烟测试通过")


if __name__ == "__main__":
    asyncio.run(main())
