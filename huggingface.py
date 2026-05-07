import requests

def get_trending():
    res = requests.get("https://huggingface.co/api/trending", timeout=30)
    res.raise_for_status()
    return {item["repoData"]["id"]: item for item in res.json()["recentlyTrending"]
            if item["repoType"] == "model"}

def get_model_details(model_id):
    info_res = requests.get(f"https://huggingface.co/api/models/{model_id}", timeout=30)
    info_res.raise_for_status()
    readme_res = requests.get(
        f"https://huggingface.co/{model_id}/resolve/main/README.md",
        timeout=30
    )
    readme = readme_res.text[:3000] if readme_res.ok else ""
    info = info_res.json()
    return info, readme
