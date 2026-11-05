# Geminiの設定、エージェントへの指示
from google.adk.agents import Agent
# github_tools.pyからget_github_repo_infoを呼び出し
from .github_tools import get_github_repo_info,get_current_repo, save_learning_level, get_learning_level
from google.adk.sessions import InMemorySessionService
from google.adk.apps.app import App, EventsCompactionConfig

from google.adk.plugins.logging_plugin import LoggingPlugin
from .observability_plugin import RepoObservabilityPlugin
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import preload_memory


from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

# 別プロセスの子エージェントを、親が呼べるツールにする。
code_explorer_tool = AgentTool(agent=RemoteA2aAgent(
	name="code_explorer",
	description="GitHubのコード本文を調べ、処理や構造を根拠付きで説明する。",
	agent_card="http://127.0.0.1:8002/.well-known/agent-card.json",
))


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
	コードの実装、実行入口、下位ディレクトリ、関数の役割を調べる場合はcode_explorerツールを使ってください。
	依頼には必ずGitHubリポジトリのURLと具体的な質問を含めてください。
	URLが省略されていたらget_current_repoで確認し、未設定ならユーザーに確認してください。
	子が返した根拠と未確認事項を保ち、ユーザーの習熟度に合わせて説明してください。
	子に接続できない場合はその旨を伝え、コード本文を確認したように答えないでください。
	""",
	tools = [get_github_repo_info,get_current_repo,save_learning_level, get_learning_level,preload_memory,code_explorer_tool
	],
	after_agent_callback=auto_save_to_memory,
)

# repo_agentをほかのエージェントから呼び出せるようにするための処理
a2a_app = to_a2a(root_agent, port=8001)

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
