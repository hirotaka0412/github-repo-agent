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
- ユーザーの情報を保存

## 起動方法

PowerShellでプロジェクトのルートに移動し、ADK Web UIを起動します。

```powershell
Set-Location C:\Users\hirot\Projects_local\kaggle\gitLearn
.\.venv\Scripts\adk.exe web --log_level INFO
```

起動後、ターミナルに表示されるURL（通常は `http://127.0.0.1:8000`）をブラウザで開き、エージェント一覧から `repo_agent` を選択します。既存の起動コマンドでセッションやメモリの設定オプションを指定している場合は、それらも引き継いでください。停止する場合は、ターミナルで `Ctrl+C` を押します。

詳細なログを確認する場合は、ログレベルを `DEBUG` に変更して起動します。

```powershell
.\.venv\Scripts\adk.exe web --log_level DEBUG
```

ログをファイルにも保存する場合は、次のコマンドを使います。

```powershell
New-Item -ItemType Directory -Force logs | Out-Null
.\.venv\Scripts\adk.exe web --log_level INFO 2>&1 |
    Tee-Object -FilePath logs\adk.log -Append
```

ログには会話やツールの内容が含まれる場合があるため、共有前に内容を確認してください。

## 確認方法

1. Web UIで `repo_agent` を選択し、「https://github.com/google/adk-python の概要を教えてください」と入力します。
2. 起動したターミナルで、`LoggingPlugin` の実行ログと、独自プラグインの次のログを確認します。IDと累計回数は実行状況によって変わります。

   ```text
   [Tool start] invocation_id=... tool=get_github_repo_info session_total=1
   [Tool end] invocation_id=... tool=get_github_repo_info status=success
   ```

3. 同じセッションで「get_current_repoツールで保存済みのリポジトリ情報を確認してください」と入力し、ツールが呼ばれると `session_total` が増えることを確認します。
4. 新しいセッションを作成して再度リポジトリの調査を依頼し、最初のツール呼び出しが `session_total=1` になることを確認します。

`session_total` はセッション内のツール呼び出し試行回数です。失敗した呼び出しも含み、1回のツール実行内で行われる複数のHTTPリクエストはまとめて1回として数えます。ツールが `status=error` を返す場合は `[Tool end]` にその状態が記録され、ツールが例外を発生させた場合は `[Tool exception]` が記録されます。

# day1 geminiAPI + GoogleADKで基本機能を実装
基礎となるファイル構成を実装し、APIキーやGoogleADKを使用可能な状態にする。
->レポジトリ内のファイルREADME.mdを渡すとファイルの概要を説明することが可能になった。

# day2 GitHub APIと連携
GitHub APIにアクセスするPython関数をADKのツールとして登録する。GitHubのURLを入力するだけでレポジトリの情報を自動取得して説明できるAIエージェントに拡張する。
->GitHubのURLから情報を入手するツールを作成し、回答を作成できるようになった。

# day3 会話履歴とMemoryの実装(Session, Memory)
エージェントに、現在調査しているレポジトリや過去の分析結果を記憶させる。\\
day3a:Sessionの実装完了。同じセッション内の文脈保持とユーザーの固有情報を保存できるようになった。

day3b:Memoryの実装完了。Sessionをまたいだ情報の保存ができるようになった。

# day4 エージェントの評価・改善(Agent Quality)
エージェントが正確にコードを理解できているか評価する。

day4a:プラグインの実装。既存のAppにLoggingPluginを登録。

# day5 WebUIと完成版の作成(Prototype to Production)
ブラウザ上から利用できるようにする。
