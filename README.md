# GitHubレポジトリ理解エージェント

kaggleの「5-Day AI Agents Intensive Course with Google」に並行して独自で作成したAIエージェントです。day1からday5にかけて少しずつ内容を追加しています。

## 使用技術
- Python
- Google Agent Development Kit (ADK)
- Gemini API

## 現在の機能
- Gemini APIとの接続
- ADK Web UIを使用した対話
- URLからGitHubレポジトリの情報を取得

# day1 geminiAPI + GoogleADKで基本機能を実装
基礎となるファイル構成を実装し、APIキーやGoogleADKを使用可能な状態にする。
->レポジトリ内のファイルREADME.mdを渡すとファイルの概要を説明することが可能になった。

# day2 GitHub APIと連携
GitHub APIにアクセスするPython関数をADKのツールとして登録する。GitHubのURLを入力するだけでレポジトリの情報を自動取得して説明できるAIエージェントに拡張する。
->GitHubのURLから情報を入手するツールを作成し、回答を作成できるようになった。

# day3 会話履歴とMemoryの実装(Session, Memory)
エージェントに、現在調査しているレポジトリや過去の分析結果を記憶させる。

# day4 エージェントの評価・改善(Agent Quality)
エージェントが正確にコードを理解できているか評価する。

# day5 WebUIと完成版の作成(Prototype to Production)
ブラウザ上から利用できるようにする。