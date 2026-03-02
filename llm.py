import requests
import os

class LLMProvider:
    def summarize(self, model_id, info, readme):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

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
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = res.json()
        if "choices" not in data:
            return f"Error: API returned {data.get('error', 'unknown error')}"
        return data["choices"][0]["message"]["content"]

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key, model="claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model = model

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
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = res.json()
        if "content" not in data:
            return f"Error: Anthropic API returned {data.get('error', 'unknown error')}"
        return data["content"][0]["text"]

class GoogleProvider(LLMProvider):
    def __init__(self, api_key, model="gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    def summarize(self, model_id, info, readme):
        prompt = f"""
모델 ID: {model_id}
태스크: {info.get('pipeline_tag', '알 수 없음')}
태그: {info.get('tags', [])}
README 일부:
{readme[:2000]}

위 정보를 바탕으로 이 모델이 어떤 모델인지 한국어로 3줄 이내로 요약해줘.
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        res = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
        )
        data = res.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Error: Google API returned {data.get('error', 'unknown error')}"

def get_llm_provider():
    provider_type = os.environ.get("LLM_PROVIDER", "openai").lower()
    model = os.environ.get("LLM_MODEL")
    base_url = os.environ.get("LLM_BASE_URL")

    if provider_type == "openai":
        api_key = os.environ.get("OPENAI_KEY") or os.environ.get("LLM_KEY")
        return OpenAIProvider(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
            model=model or "gpt-4o-mini"
        )
    elif provider_type == "anthropic":
        api_key = os.environ.get("ANTHROPIC_KEY") or os.environ.get("LLM_KEY")
        return AnthropicProvider(
            api_key=api_key,
            model=model or "claude-3-5-sonnet-20240620"
        )
    elif provider_type in ["google", "gemini"]:
        api_key = os.environ.get("GEMINI_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("LLM_KEY")
        return GoogleProvider(
            api_key=api_key,
            model=model or "gemini-1.5-flash"
        )
    else:
        # Generic OpenAI compatible provider as fallback for unknown types
        api_key = os.environ.get("LLM_KEY") or os.environ.get("OPENAI_KEY")
        return OpenAIProvider(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
