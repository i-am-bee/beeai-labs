import requests

def get_java_file_urls(owner: str, repo: str, branch: str = "main") -> list[str]:
    """
    Retrieve raw.githubusercontent.com URLs for all .java files in a GitHub repo
    by using the Git Trees API with recursion.
     :param owner: GitHub org/user name (e.g., "Mastercard")
    :param repo: Repository name (e.g., "client-encryption-java")
    :param branch: Branch name (default: "main")
    :param token: GitHub Personal Access Token (optional for private repos or rate limiting)
    :return: List of raw.githubusercontent.com URLs for each .java file
    """

    tree_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

    response = requests.get(tree_api_url)
    response.raise_for_status()
    tree_data = response.json().get("tree", [])

    java_urls = []
    for entry in tree_data:
        if entry.get("type") == "blob" and entry.get("path", "").endswith(".java"):
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{entry['path']}"
            java_urls.append(raw_url)

    return java_urls

