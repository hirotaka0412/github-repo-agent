# 作成するファイルとその構成

## 処理の流れ
全体の処理の流れは以下のようになる。

```Mermaid
flowchart LR
    A["React / テスト画面"] --> B["main.py"]
    B --> C["agent_service.py"]
    C --> D["repo_agent/agent.py"]
    D --> E["Gemini・GitHub"]
```
各ファイルの役割を以下に示す。

| ファイル | 役割 |
|---|---|
| `backend/__init__.py` | `backend` をPythonのパッケージとして扱う |
| `backend/main.py` | ReactからのHTTPリクエストを受け付ける |
| `backend/schemas.py` | リクエストとレスポンスのデータ形式を定義する |
| `backend/agent_service.py` | ADKのセッションを作成し、エージェントを実行する |
| `repo_agent/agent.py` | 既存のエージェントの指示・ツール・プラグインを定義する |

