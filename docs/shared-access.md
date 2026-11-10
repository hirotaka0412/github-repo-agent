# 共通パスワードでの共有

## 仕組み

FastAPI の SharedPasswordMiddleware が画面、静的ファイル、/api/chat、/docs を HTTP Basic 認証で保護します。ブラウザ標準のダイアログにユーザー名とパスワードを入力します。HTTPS の Cloud Run URL から使用してください。子の A2A サーバーは内部ポート8002のままです。

- SHARED_USERNAME: 既定は guest
- SHARED_PASSWORD: 16文字以上。Secret Manager から api コンテナに渡す
- 設定漏れ・短すぎるパスワード: 503で拒否
- /api/health の GET/HEAD のみ、プローブ用に認証不要

これは個別アカウントではありません。利用者ごとの失効や回数上限はありません。最大インスタンス数1も累積料金の上限にはなりません。共有を止める場合は Cloud Run の IAM 認証を再び必須にします。パスワード変更後は再デプロイが必要です。ブラウザは認証情報を保持するため、共有PCではプライベートウィンドウを使用して終了時に閉じてください。

## 1. 共有パスワードを登録（Cloud Run）

Secret Manager で gitlearn-shared-password を作成し、パスワードマネージャーで生成したランダムなASCII文字のパスワード（20文字以上推奨）の値だけを保存します。Gemini APIキーとは別のシークレットです。チャットやソースコードへ貼り付けないでください。

PowerShell:

```powershell
gcloud secrets add-iam-policy-binding gitlearn-shared-password --member="serviceAccount:gitlearn-runtime@gitlearn-hirot-20261106.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=gitlearn-hirot-20261106
```

## 2. ビルド・アップロード

```powershell
Set-Location C:\Users\hirot\Projects_local\kaggle\gitLearn
$imageUri = 'asia-northeast1-docker.pkg.dev/gitlearn-hirot-20261106/gitlearn/app:v4'
docker build -t gitlearn:local .
docker tag gitlearn:local $imageUri
docker push $imageUri
```

## 3. IAM認証を維持してデプロイ

Cloud Run の gitlearn の編集画面で両コンテナを v4 に変更します。

api コンテナに次を追加します。

- 通常の環境変数 SHARED_USERNAME = guest
- シークレット参照 SHARED_PASSWORD = gitlearn-shared-password のバージョン1

既存の GOOGLE_API_KEY、GOOGLE_GENAI_USE_VERTEXAI、起動順序、起動プローブ、ポートは維持します。共有パスワードは explorer には不要です。認証必須のままデプロイします。

## 4. 公開前の確認

```powershell
gcloud run services proxy gitlearn --region=asia-northeast1 --project=gitlearn-hirot-20261106 --port=19090
```

プライベートウィンドウで http://127.0.0.1:19090/ を開き、認証ダイアログが出ること、正しい認証情報で画面と質問送信が動くことを確認します。

別の PowerShell から、認証なしのAPI呼び出しが401になることを確認します（Gemini呼び出しは発生しません）。

```powershell
curl.exe -i -X POST http://127.0.0.1:19090/api/chat -H 'Content-Type: application/json' --data-raw '{}'
```

## 5. 共有URLを有効にする

手順4の確認後だけ、Cloud Run のセキュリティで公開アクセスを許可します。Google Cloud IAMの入口認証を解除し、アプリの共通パスワードで保護する構成です。

```powershell
gcloud run services update gitlearn --region=asia-northeast1 --project=gitlearn-hirot-20261106 --no-invoker-iam-check
gcloud run services describe gitlearn --region=asia-northeast1 --project=gitlearn-hirot-20261106 --format='value(status.url)'
```

表示された https://...run.app のURLをプライベートウィンドウで開き、認証なしでは入れないことと、認証後の質問送信を確認します。URLと共通ユーザー名・パスワードを利用者へ伝えます。利用者のPCでCLIやプロキシを起動する必要はありません。

## ローカル開発

FastAPI 起動前に SHARED_USERNAME と SHARED_PASSWORD を環境変数またはプロジェクト直下の .env に設定してください。.env はGitやDockerイメージに含めません。ローカル開発用の別パスワードを使用してください。

## テスト

```powershell
.\.venv\Scripts\python.exe -m unittest backend.test_shared_auth
```
