import requests
import os

class LLMProvider:
    def _build_prompt(self, model_id, info, readme):
        return f"""
Hugging Face 트렌딩 모델 요약 요청입니다.

모델 ID: {model_id}
태스크: {info.get('pipeline_tag', '알 수 없음')}
태그: {info.get('tags', [])}
README (최초 2000자):
{readme[:2000]}

---
[요약 지침]
- 위 정보를 바탕으로 모델의 핵심 특징, 기술적 차별점, 주요 활용 사례를 한국어로 요약하세요.
- 반드시 3개의 항목으로 구성된 번호 리스트(1., 2., 3.) 형식을 사용하세요.
- 각 항목은 한 문장으로 간결하게 작성하세요.
- "이 모델은...", "요약해 드립니다"와 같은 서론이나 결론은 완전히 생략하고 요약 내용만 출력하세요.
- 마크다운 볼드(**) 등 불필요한 서식을 최소화하여 가독성을 높이세요.
"""

    def summarize(self, model_id, info, readme):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, model_id, info, readme):
        prompt = self._build_prompt(model_id, info, readme)
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
        prompt = self._build_prompt(model_id, info, readme)
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
        prompt = self._build_prompt(model_id, info, readme)
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
    provider_type = (os.environ.get("LLM_PROVIDER") or "openai").strip().lower()
    model = (os.environ.get("LLM_MODEL") or "").strip() or None
    base_url = (os.environ.get("LLM_BASE_URL") or "").strip() or None

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
            base_url=base_url or "https://api.openai.com/v1",
            model=model or "gpt-4o-mini"
        )
