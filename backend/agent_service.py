# 既存のrepo_agent.agentにあるappを使ってADKを実行する

# 現在のAppにはログ用プラグインや履歴圧縮設定が含まれているため、単にroot_agentを取り出すのではなく、appをRunnerに渡す。

# uuid : ソフトウェア上でオブジェクトを一意に識別するための識別子。重複が起こらない。
import uuid

from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from repo_agent.agent import app as agent_app

# エージェントを動かす関数
async def run_agent(message: str) -> str:
	# asyncは並列実行（非同期処理）が可能な関数。
	"""
	ADKエージェントを1回実行し、最終返答を返す。

	この試作版では、リクエストごとに新しいセッションを作る。
	前回の質問は引き継がない。
	"""

	# リクエスト毎に一時的な保存領域を作る。
	session_service = InMemorySessionService() 
	memory_service = InMemoryMemoryService()

	# 既存のAppを使ってRunnerを作成
	runner = Runner(
		app = agent_app,
		session_service = session_service,
		memory_service = memory_service,
	)

	# この試作版では、毎回異なるIDを作成
	user_id = str(uuid.uuid4())
	session_id = str(uuid.uuid4())

	# ADKの会話セッションを作成
	"非同期処理の完了を待つ間、他の処理に実行を譲る"
	await session_service.create_session(
		app_name=agent_app.name,
		user_id=user_id,
		session_id=session_id,
	)

	# ユーザーの文字列をADKが扱うメッセージ形式に変換する。
	user_message = types.Content(
		role = "user",
		parts=[
			types.Part(text=message)
		],
	)

	# 将来的に回答を格納する空リスト
	answer_parts = []

	# エージェントを実行し、生成されるイベントを順に受け取る。
	async for event in runner.run_async(
		user_id = user_id,
		session_id = session_id,
		new_message = user_message,
	):
		if event.is_final_response() and event.content:
			for part in event.content.parts or []:
				if part.text:
					answer_parts.append(part.text)

	if not answer_parts:
		raise RuntimeError("エージェントから最終回答を取得できませんでした。")

	return "\n".join(answer_parts)