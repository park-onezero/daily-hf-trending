import requests

def get_trending():
    res = requests.get("https://huggingface.co/api/trending")
    return {item["repoData"]["id"]: item for item in res.json()["recentlyTrending"]
            if item["repoType"] == "model"}

def get_model_details(model_id):
    info = requests.get(f"https://huggingface.co/api/models/{model_id}").json()
    readme = requests.get(
        f"https://huggingface.co/{model_id}/resolve/main/README.md"
    ).text[:3000]
    return info, readme
