# GitHub APIへのアクセスと情報取得
import base64
import re
import requests
from urllib.parse import urlparse

GITHUB_API = "https://api.github.com"

HEADERS = {
	"Accept": "application/vnd.github+json",
	"X-GitHub-Api-Version": "2022-11-28",
	"User-Agent": "github-repo-agent",
}

def parse_github_url(github_url: str) -> tuple[str, str]:
    """GitHubのURLからownerとrepoを取り出す。"""
    parsed = urlparse(github_url.strip())

    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise ValueError("https://github.com/owner/repo の形式で入力してください。")

    parts = parsed.path.strip("/").split("/")

    if len(parts) != 2:
        raise ValueError("リポジトリのトップページのURLを指定してください。")

    owner, repo = parts
    repo = repo.removesuffix(".git")

    pattern = r"[A-Za-z0-9_.-]+"

    if not re.fullmatch(pattern, owner) or not re.fullmatch(pattern, repo):
        raise ValueError("GitHub URLのownerまたはrepoが不正です。")

    return owner, repo


def get_github_repo_info(github_url: str) -> dict:
    """公開GitHubリポジトリの概要・README・トップ階層を取得する。

    Args:
        github_url: https://github.com/owner/repo 形式のURL。

    Returns:
        リポジトリ情報、README、ファイル一覧、取得状態。
    """
    try:
        owner, repo = parse_github_url(github_url)
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    base_url = f"{GITHUB_API}/repos/{owner}/{repo}"

    def fetch(path: str):
        return requests.get(
            f"{base_url}{path}",
            headers=HEADERS,
            timeout=15,
        )

    try:
        # ① リポジトリの基本情報
        response = fetch("")
        response.raise_for_status()
        repo_data = response.json()

        # ② トップ階層のファイル・ディレクトリ
        response = fetch("/contents")
        response.raise_for_status()
        contents = response.json()

        files = [
            {"name": item["name"], "type": item["type"]}
            for item in contents
        ]

        # ③ READMEの取得
        readme = ""
        readme_response = fetch("/readme")

        if readme_response.status_code == 200:
            readme_data = readme_response.json()

            if readme_data.get("encoding") == "base64":
                # READMEはBase64形式で返されるため元の文章に戻す
                decoded = base64.b64decode(
                    readme_data["content"]
                )
                readme = decoded.decode("utf-8", errors="replace")

        # 長すぎるREADMEは切り詰める
        if len(readme) > 12000:
            readme = readme[:12000] + "\n...(省略)"

        return {
            "status": "success",
            "name": repo_data["full_name"],
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data["stargazers_count"],
            "default_branch": repo_data["default_branch"],
            "files": files[:100],
            "readme": readme,
        }

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code

        if status == 404:
            message = "リポジトリが見つからないか、非公開です。"
        elif status in (403, 429):
            message = "GitHub APIのアクセス制限の可能性があります。"
        else:
            message = f"GitHub APIエラー: HTTP {status}"

        return {"status": "error", "message": message}

    except requests.exceptions.RequestException:
        return {
            "status": "error",
            "message": "GitHubへの通信に失敗しました。",
        }
