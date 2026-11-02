# custom plugin
# ・ツール実行前に呼び出し回数を加算
# ・ツール実行後に結果の状態を記録
# ・ツールが例外フォ発生させた際にエラーを記録 
import logging
from typing import Any

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


logger = logging.getLogger("google_adk.repo_agent.observability")


class RepoObservabilityPlugin(BasePlugin):
    """セッション内のツール呼び出し回数と実行結果を記録する。"""

    def __init__(self) -> None:
        super().__init__(name="repo_observability")

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> None:
        key = "observability:tool_call_count"
        # ツールの呼び出しの試行回数
        count = tool_context.state.get(key, 0) + 1
        tool_context.state[key] = count

        logger.info(
            "[Tool start] invocation_id=%s tool=%s session_total=%d",
            tool_context.invocation_id,
            tool.name,
            count,
        )

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        result: dict[str, Any],
    ) -> None:
        status = (
            result.get("status", "unknown")
            if isinstance(result, dict)
            else "unknown"
        )

        log = logger.warning if status == "error" else logger.info
        log(
            "[Tool end] invocation_id=%s tool=%s status=%s",
            tool_context.invocation_id,
            tool.name,
            status,
        )

    async def on_tool_error_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        error: Exception,
    ) -> None:
        logger.error(
            "[Tool exception] invocation_id=%s tool=%s error_type=%s",
            tool_context.invocation_id,
            tool.name,
            type(error).__name__,
        )