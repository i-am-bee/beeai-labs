import requests

def fetch_raw_file_content(url: str) -> str:
    """
    Fetch the full content of a raw.githubusercontent.com URL using HTTP.

    :param url: Raw file URL (e.g., https://raw.githubusercontent.com/.../AesEncrypter.java)
    :return: The file content as a text string
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

