# GitLearn フロントエンド

公開 GitHub リポジトリの URL と質問を入力し、調査結果を表示する最小構成の React 画面です。質問ごとに独立した調査を行います。回答は改行を保持したプレーンテキストで表示します。

## ローカルで起動

PowerShell のターミナル1で、認証済みの Cloud Run プロキシを起動します。

```powershell
gcloud run services proxy gitlearn --region=asia-northeast1 --project=gitlearn-hirot-20261106 --port=19090
```

ターミナル2で画面を起動します。

```powershell
Set-Location C:\Users\hirot\Projects_local\kaggle\gitLearn\frontend
npm install
npm run dev
```

Vite が表示した URL を開いてください。画面だけの確認はプロキシなしでもできます。質問送信にはプロキシが必要です。Gemini API キーをフロントエンドに設定する必要はありません。

## ローカル FastAPI に接続する場合

`frontend/.env.local` に次を設定し、Vite を再起動します。ポートは実際の起動ポートに合わせてください。

```dotenv
API_PROXY_TARGET=http://127.0.0.1:18080
```

既定の接続先は `http://127.0.0.1:19090` です。`/api` は Vite の開発サーバーから転送されます。

## 確認

```powershell
npm run lint
npm run build
```

`npm run preview` は画面のビルド確認用です。開発用 API プロキシは `npm run dev` で有効です。

## 公開について

今回はフロントエンドのみを実装しています。Cloud Run への画面配信には、Dockerfile で React をビルドして FastAPI から `dist` を配信する設定を別途追加します。ブラウザは同一オリジンの `/api/chat` を呼ぶため、公開先でもそのルートが必要です。

共通パスワード付き公開の手順は [共有手順](../docs/shared-access.md) を参照してください。ローカル FastAPI にも SHARED_PASSWORD（16文字以上）の設定が必要です。

