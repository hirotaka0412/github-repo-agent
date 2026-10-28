from google.adk.agents import Agent

root_agent = Agent(
	name = "github_repo_agent",
	model="gemini-3.8-flash",
	description="GitHubレポジトリを理解するAIエージェント",
	instruction="""
	あなたはGitHubレポジトリを分析するAIエージェントです。
	
	ユーザーの質問に対して、
	- リポジトリの概要
    - 主要な機能
    - ディレクトリ構成
    - コードの役割

    を初心者にも分かりやすく説明してください。

    不明な情報は推測せず、不明であると伝えてください。
	""",
)