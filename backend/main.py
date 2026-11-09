# HTTPリクエストを受信
import logging

# 環境変数ファイルを読み込むためのライブラリ
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# ディレクトリから静的ファイルを自動的に提供
from pathlib import Path
from fastapi.staticfiles import StaticFiles
"""
FastAPI: Python製のWebフレームワーク
- 非同期処理に対応
- 自動ドキュメント生成
- pydanticを活用してデータ検証（バリデーション・ドキュメント・エディタ補完）ができる。
- 高速なレスポンス性能
HTTPException: HTTPレスポンスをエラーでクライアントに返すのに必要。（raiseを使用）
"""

# エージェントを読み込む前に、ローカルの環境変数を設定(APIキー等を読み込み)
load_dotenv()

from backend.agent_service import run_agent
from backend.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

app = FastAPI(
	title="GitHub Repository Agent API",
	description="GitHubレポジトリ理解エージェントのAPI",
	version="1.0.0",
)

# APIサーバーが起動しているか確認
@app.get("/api/health")
async def health_check():
	"APIサーバーの起動確認"
	return {"status": "ok"}

# HTTPメソッド: 質問を送信し、回答を受け取る
@app.post("/api/chat")
async def chat(request: ChatRequest):
	"質問を受けとり、エージェントの解答を返す。"

	message = request.message.strip()

	if not message:
		raise HTTPException(
			status_code = 422,
			detail="質問を入力してください。"
		)

	try:
		answer = await run_agent(message)
	except Exception:
		# 詳細はサーバー側に記録し、利用者には表示しない。
		logger.exception("エージェントの実行に失敗しました。")

		raise HTTPException(
			status_code = 500,
			detail = "エージェントの実行中にエラーが発生しました。"
		)
	return ChatResponse(answer = answer)

# Reactのビルド結果を配信する
frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"

if frontend_dist.is_dir():
	app.mount(
		"/",
		StaticFiles(directory=str(frontend_dist), html = True),
		name="frontend",
	)