import os, json
from huggingface import get_trending, get_model_details
from llm import get_llm_provider
from slack import notify_slack

CACHE_FILE = "trending_cache.json"

# 1. 이전 캐시 불러오기
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

# 2. diff: 새로 추가된 모델만 추출
def get_new_models(current, cached):
    return {k: v for k, v in current.items() if k not in cached}

def main():
    # 메인
    current = get_trending()
    cached = load_cache()
    new_models = get_new_models(current, cached)

    if not new_models:
        print("새로운 트렌딩 모델이 없습니다.")
        return

    provider = get_llm_provider()

    for model_id, _ in new_models.items():
        print(f"처리 중: {model_id}")
        info, readme = get_model_details(model_id)
        summary = provider.summarize(model_id, info, readme)
        notify_slack(model_id, summary, info)

    # 캐시 업데이트
    with open(CACHE_FILE, "w") as f:
        json.dump(current, f)

if __name__ == "__main__":
    main()
