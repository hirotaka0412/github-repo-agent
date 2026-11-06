# APIで受け取るデータと返すデータを定義する.
# ReactとはJsonを送受信

# データ構造化を容易にするライブラリから
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
	# 利用者から受け取る質問

	message: str = Field(
		min_length = 1,
		max_length = 4000,
		descripton = "エージェントへの質問",
	)

class ChatResponse(BaseModel):
	# エージェントから返す返答

	answer : str