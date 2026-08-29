import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _text(result) -> str:
    return "".join(
        item.text for item in result.content if getattr(item, "type", "") == "text"
    )


def test_stdio_round_trip_uses_active_python_interpreter() -> None:
    async def run() -> None:
        child_env = os.environ.copy()
        child_env["PYTHONIOENCODING"] = "utf-8"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "cys_prompt_suite.server"],
            env=child_env,
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert len(tools.tools) == 9

                result = await session.call_tool(
                    "check_prompt",
                    {
                        "prompt": "国风长裙成年女性，全身入镜，鞋履完整",
                        "content_type": "real",
                        "platform": "douyin",
                    },
                )
                payload = json.loads(_text(result))
                assert payload["summary"]["passed"] is True

    asyncio.run(run())
