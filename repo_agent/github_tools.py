# 1.GitHub APIへのアクセスと情報取得
import base64
import re
import requests
from urllib.parse import urlparse
from google.adk.tools.tool_context import ToolContext

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


def get_github_repo_info(
        github_url: str,
        tool_context: ToolContext,
        ) -> dict:
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

        result = {
            "status": "success",
            "name": repo_data["full_name"],
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data["stargazers_count"],
            "default_branch": repo_data["default_branch"],
            "files": files[:100],
            "readme": readme,
        }

        # 取得に成功したときのみ調査対象を更新する
        tool_context.state["current_repo_url"] = (
            f"https://github.com/{owner}/{repo}"
        )
        tool_context.state["current_repo_info"] = result
        return result

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

# 2.保存済み情報を読むツール
def get_current_repo(tool_context: ToolContext)->dict:
    repo_info = tool_context.state.get("current_repo_info")

    if repo_info is None:
        return {
            "states": "not_found",
            "message": "調査するGitHubレポジトリのURLを教えてください。",
        }
    return {
        "status": "success",
        "url": tool_context.state.get("current_repo_url"),
        "repo_info": repo_info,
    }

# 別Sessionでも共有するユーザー設定を追加
def save_learning_level(
        learning_level: str,
        tool_context: ToolContext,
) -> dict:
    # ユーザーのGit習熟度を保存する。初心者・中級者・上級者から選択
    if learning_level not in ("初心者","中級者","上級者"):
        return {
            "status": "error",
            "message": "初心者・中級者・上級者から選んでください。",
        }
    tool_context.state["user:learning_level"] = learning_level
    return {"status": "success", "learning_level": learning_level}

def get_learning_level(tool_context: ToolContext) -> dict:
    # 保存済みのGit習熟度を取得する。
    return {
        "learning_level": tool_context.state.get(
            "user:learning_level", "未設定"
        )

    }