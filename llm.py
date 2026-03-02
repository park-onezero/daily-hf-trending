import requests
import os

class LLMProvider:
    def summarize(self, model_id, info, readme):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def summarize(self, model_id, info, readme):
        prompt = f"""
모델 ID: {model_id}
태스크: {info.get('pipeline_tag', '알 수 없음')}
태그: {info.get('tags', [])}
README 일부:
{readme[:2000]}

위 정보를 바탕으로 이 모델이 어떤 모델인지 한국어로 3줄 이내로 요약해줘.
"""
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
        )
        data = res.json()
        if "choices" not in data:
            return f"Error: OpenAI API returned {data.get('error', 'unknown error')}"
        return data["choices"][0]["message"]["content"]

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def summarize(self, model_id, info, readme):
        prompt = f"""
모델 ID: {model_id}
태스크: {info.get('pipeline_tag', '알 수 없음')}
태그: {info.get('tags', [])}
README 일부:
{readme[:2000]}

위 정보를 바탕으로 이 모델이 어떤 모델인지 한국어로 3줄 이내로 요약해줘.
"""
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = res.json()
        if "content" not in data:
            return f"Error: Anthropic API returned {data.get('error', 'unknown error')}"
        return data["content"][0]["text"]

def get_llm_provider():
    provider_type = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider_type == "openai":
        return OpenAIProvider(os.environ.get("OPENAI_KEY"))
    elif provider_type == "anthropic":
        return AnthropicProvider(os.environ.get("ANTHROPIC_KEY"))
    else:
        raise ValueError(f"지원하지 않는 LLM 프로바이더: {provider_type}")
