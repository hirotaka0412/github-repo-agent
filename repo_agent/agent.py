# Geminiの設定、エージェントへの指示
from google.adk.agents import Agent
# github_tools.pyからget_github_repo_infoを呼び出し
from .github_tools import get_github_repo_info,get_current_repo, save_learning_level, get_learning_level
from google.adk.sessions import InMemorySessionService
from google.adk.apps.app import App, EventsCompactionConfig

from google.adk.plugins.logging_plugin import LoggingPlugin
from .observability_plugin import RepoObservabilityPlugin

from google.adk.tools import preload_memory
# Memory検索と自動保存
async def auto_save_to_memory(callback_context):
	await callback_context.add_session_to_memory()

# day3a Sessionの実装
# 以下ユーザー情報
APP_NAME = "default"
USER_ID = "default"
SESSION = "default" 

MODEL_NAME = "gemini-3.8-flash"

root_agent = Agent(
	name = "github_repo_agent",
	model="gemini-3.8-flash",
	description="GitHubレポジトリを理解するAIエージェント",
	instruction="""
	あなたはGitHubレポジトリを分析するAIエージェントです。
	
	ユーザーの質問に対して、
	- リポジトリの概要
	- 使用されているプログラミング言語
    - 主要な機能
    - ディレクトリ構成
    - コードの役割

    を初心者にも分かりやすく説明してください。

	回答は質問された言語に準拠してください。

	ツールで取得できなかった情報は推測しないでください。ファイル名だけで役割や機能を断定できない場合、推測であることを明記してください。

	ユーザーがGitの習熟度を明示したら、save_learning_levelで保存してください。
	GitやGitHubの説明前にはget_learning_levelで習熟度を確認し、
	説明の詳しさを調整してください。
	未設定の場合は初心者向けに説明してください。

	過去の調査内容について質問された場合は、Memoryの検索結果を参考にしてください。
	現在のリポジトリ情報が必要な場合は、GitHubの取得ツールで確認してください。
	""",
	tools = [get_github_repo_info,get_current_repo,save_learning_level, get_learning_level,preload_memory
	],
	after_agent_callback=auto_save_to_memory,
)

# root_agentを包むAppに、履歴の圧縮を設定する。
app = App(
	name = "repo_agent",
	root_agent = root_agent,

	plugins=[
		LoggingPlugin(),
		RepoObservabilityPlugin(),
	],
	
	events_compaction_config = EventsCompactionConfig(
		# 3回の呼び出しごとに履歴を圧縮
		compaction_interval = 3,
		# 圧縮する範囲の会話に前の会話を１ターン重ね、文脈のつながりを保つ。
		overlap_size = 1,
	),
)