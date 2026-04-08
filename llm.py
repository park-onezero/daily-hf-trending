import requests
import os

class LLMProvider:
    def _stringify(self, value):
        if value in (None, "", [], {}):
            return "미상"
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            return ", ".join(cleaned[:5]) if cleaned else "미상"
        return str(value).strip() or "미상"

    def _extract_tag_values(self, tags, prefix):
        values = []
        for tag in tags or []:
            if isinstance(tag, str) and tag.startswith(prefix):
                value = tag[len(prefix):].strip()
                if value:
                    values.append(value)
        return values

    def _collect_facts(self, info, readme):
        tags = info.get("tags") or []
        card_data = info.get("cardData") or {}
        config = info.get("config") or {}

        license_name = (
            info.get("license")
            or card_data.get("license")
            or self._extract_tag_values(tags, "license:")
        )
        languages = (
            card_data.get("language")
            or self._extract_tag_values(tags, "language:")
        )
        base_models = (
            card_data.get("base_model")
            or self._extract_tag_values(tags, "base_model:")
        )

        interesting_tags = []
        for tag in tags:
            if not isinstance(tag, str):
                continue
            if ":" in tag:
                continue
            if tag in {"transformers", "safetensors", "endpoints_compatible"}:
                continue
            interesting_tags.append(tag)

        file_traits = [
            trait for trait in interesting_tags
            if trait in {
                "gguf", "gptq", "awq", "onnx", "mlx", "4-bit", "8-bit",
                "text-generation-inference", "diffusers"
            }
        ]

        facts = {
            "태스크": info.get("pipeline_tag"),
            "라이브러리": info.get("library_name"),
            "라이선스": license_name,
            "언어": languages,
            "베이스 모델": base_models,
            "아키텍처": config.get("architectures"),
            "파일/배포 특성": file_traits,
            "대표 태그": interesting_tags[:8],
            "모델 카드 요약 원문": readme[:2000] if readme else "없음",
        }
        return "\n".join(
            f"- {key}: {self._stringify(value)}" for key, value in facts.items()
        )

    def _build_prompt(self, model_id, info, readme):
        facts = self._collect_facts(info, readme)
        return f"""
Hugging Face 트렌딩 모델 Slack 알림용 요약 요청입니다.
목표는 "이 모델이 왜 지금 볼 만한지"를 빠르게 파악하게 만드는 것입니다.

모델 ID: {model_id}
확인된 메타데이터:
{facts}

---
[요약 지침]
- 반드시 아래 4개 라벨만 사용해 정확히 4줄로 출력하세요.
  - 정체성:
  - 핵심:
  - 용도:
  - 주의:
- 각 줄은 한 문장만 쓰고, 90자 안팎으로 짧게 유지하세요.
- 초보자용 일반론, 홍보 문구, 막연한 장점은 금지합니다.
- "유용합니다", "빠릅니다", "정확합니다", "고성능", "강화", "적합", "누구나 쉽게" 같은 표현은 근거가 있을 때만 쓰세요.
- 태스크명을 풀어쓰는 수준의 설명만 반복하지 마세요.
- 베이스 모델, 배포 포맷(GGUF/GPTQ/AWQ 등), 언어, 라이선스, 입력/출력 형태, 문서화된 특징이 있으면 우선 반영하세요.
- 메타데이터에서 직접 확인되는 사실과 README 주장/소개 문구를 구분하세요.
- README에서만 확인되는 주장, 벤치마크, 권장 하드웨어, 성능 수치, 학습 방식은 반드시 "README 기준", "모델 카드 기준" 같은 표현을 붙이세요.
- 메타데이터에서 직접 확인되지 않는 추천/운영 가이드는 만들지 마세요.
- "용도:"는 추천 문구가 아니라 대표 사용 시나리오를 중립적으로 한 줄 설명하세요.
- 하드웨어 요구사항, 속도 비교, 벤치마크 점수, "제한 없음", "검열 해제", "보안/펜테스팅 강화" 같은 민감하거나 강한 표현은 README에 명시된 경우에만 쓰세요.
- 확인되지 않은 내용은 추측하지 말고 "README/메타데이터 기준 미상"처럼 명시하세요.
- 상단 메타 정보(좋아요, 크기, 파라미터)를 반복하지 마세요.
- `정체성:`은 모델의 계열/포맷/기반 모델처럼 식별 가능한 사실 위주로 쓰세요.
- `핵심:`은 차별점 1개만 쓰고, README 주장이라면 그 사실을 드러내세요.
- 출력에는 서론, 결론, 번호 목록, 마크다운 볼드, 빈 줄을 넣지 마세요.
"""

    def summarize(self, model_id, info, readme):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, model_id, info, readme):
        if not self.api_key:
            return "Error: Missing API key (set OPENROUTER_API_KEY or LLM_KEY/OPENAI_KEY)."
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
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")

    if provider_type == "openai":
        api_key = os.environ.get("OPENAI_KEY") or openrouter_key or os.environ.get("LLM_KEY")
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
        api_key = (
            os.environ.get("GEMINI_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or openrouter_key
            or os.environ.get("LLM_KEY")
        )
        if base_url:
            # Allow using OpenRouter (OpenAI-compatible) while keeping google/gemini provider selection.
            return OpenAIProvider(
                api_key=api_key,
                base_url=base_url,
                model=model or "google/gemma-4-31b-it:free"
            )
        return GoogleProvider(
            api_key=api_key,
            model=model or "gemini-1.5-flash"
        )
    else:
        # Generic OpenAI compatible provider as fallback for unknown types
        api_key = os.environ.get("LLM_KEY") or os.environ.get("OPENAI_KEY") or openrouter_key
        return OpenAIProvider(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
            model=model or "gpt-4o-mini"
        )
