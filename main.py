import sys
import os
import re
import webbrowser
import json
from pathlib import Path

# --- 設定：パスを書き換えてください ---
# Windowsのパスは r"C:\path\to\vault" のように r を付けるか、スラッシュ / を使ってください
VAULT_PATH = r"C:\Users\username\Documents\Obsidian\Vault1"
# ------------------------------------


def get_links_from_vault(query=""):
    results = []

    if not os.path.exists(VAULT_PATH):
        return [
            {
                "Title": "Error",
                "SubTitle": f"Vault path not found: {VAULT_PATH}",
                "IcoPath": "",
            }
        ]

    try:
        # Vault内の全Markdownファイルを走査
        for path in Path(VAULT_PATH).rglob("*.md"):
            try:
                # ファイルが大きすぎる場合の安全策（任意）
                if path.stat().st_size > 1024 * 1024:
                    continue

                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # フロントマター抽出
                    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                    if not match:
                        continue

                    frontmatter = match.group(1)
                    links = re.findall(r"([\w_-]+):\s*(https?://[^\s\n]+)", frontmatter)

                    file_title = path.stem
                    for key, url in links:
                        search_text = f"{file_title} {key} {url}".lower()
                        if not query or query.lower() in search_text:
                            results.append(
                                {
                                    "Title": f"{file_title} ({key})",
                                    "SubTitle": f"Open: {url}",
                                    "IcoPath": "icon.png",
                                    "JsonRPCAction": {
                                        "method": "open_url",
                                        "parameters": [url],
                                    },
                                }
                            )
            except Exception:
                continue
    except Exception as e:
        return [{"Title": "Python Error", "SubTitle": str(e), "IcoPath": ""}]

    if not results:
        results.append(
            {
                "Title": "No links found",
                "SubTitle": "Try a different search term",
                "IcoPath": "",
            }
        )

    return results


def open_url(url):
    webbrowser.open(url)


if __name__ == "__main__":
    try:
        # 引数がない場合は空の結果を返す（デバッグ用）
        if len(sys.argv) < 2:
            print(json.dumps({"result": [{"Title": "No arguments"}]}))
            sys.exit()

        rpc_request = json.loads(sys.argv[1])
        method = rpc_request.get("method")
        params = rpc_request.get("parameters", [])

        if method == "query":
            query = params[0] if params else ""
            results = get_links_from_vault(query)
            print(json.dumps({"result": results}))

        elif method == "open_url":
            open_url(params[0])

    except Exception as e:
        # エラーが起きた場合、Flow Launcherが解釈できる形式でエラーを返す
        print(
            json.dumps(
                {
                    "result": [
                        {
                            "Title": "Critical Script Error",
                            "SubTitle": str(e),
                            "IcoPath": "icon.png",
                        }
                    ]
                }
            )
        )
