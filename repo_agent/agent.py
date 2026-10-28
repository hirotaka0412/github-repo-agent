# Geminiの設定、エージェントへの指示
from google.adk.agents import Agent
# github_tools.pyからget_github_repo_infoを呼び出し
from .github_tools import get_github_repo_info


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
	""",
	tools = [get_github_repo_info],
)