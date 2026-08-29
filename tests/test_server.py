import asyncio

from fastmcp import Client

from cys_prompt_suite import server


def test_all_tools_are_registered_and_callable_in_memory() -> None:
    async def run() -> None:
        async with Client(server.mcp) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools}
            assert names == {
                "generate_portrait_prompt",
                "generate_anime_prompt",
                "generate_h3_prompt",
                "check_prompt",
                "self_check_list",
                "explain_rule",
                "list_platforms",
                "generate_and_check",
                "list_prompt_options",
            }

            direct_calls = {
                "generate_portrait_prompt": {},
                "generate_anime_prompt": {},
                "generate_h3_prompt": {
                    "mode": "T2VA",
                    "integrated_multimodal_description": "A stable continuous shot.",
                },
                "check_prompt": {"prompt": "成年角色，全身构图"},
                "self_check_list": {},
                "explain_rule": {"rule_id": "BANNED"},
                "list_platforms": {},
            }
            for tool_name, arguments in direct_calls.items():
                response = await client.call_tool(tool_name, arguments)
                assert response.data is not None, tool_name

            result = await client.call_tool(
                "generate_and_check",
                {
                    "kind": "anime",
                    "family": "国风仙侠",
                    "use_wordbank": True,
                    "seed": 3,
                },
            )
            assert result.data["safe_passed"] is True
            assert result.data["requires_human_review"] is True

            h3_result = await client.call_tool(
                "generate_and_check",
                {
                    "kind": "h3",
                    "h3_mode": "FL2VA",
                    "duration_seconds": 6,
                    "first_frame_desc": "an adult performer at rest",
                    "last_frame_desc": "the same performer in a final pose",
                    "integrated_multimodal_description": "One continuous controlled turn.",
                },
            )
            assert "6.00-second mark" in h3_result.data["prompt"]

            options = await client.call_tool("list_prompt_options", {})
            assert "原神" not in options.data["wordbank_anime_families"]
            assert "原神" in options.data["third_party_ip_families"]

    asyncio.run(run())
