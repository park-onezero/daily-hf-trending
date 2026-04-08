# Daily Hugging Face Trending Monitor

Hugging Face의 일일 트렌딩 모델을 모니터링하고, LLM을 사용하여 요약한 뒤 Slack으로 알림을 보내는 도구입니다.

## 환경 변수 설정 (Environment Variables)

프로젝트 실행을 위해 다음 환경 변수들을 설정해야 합니다. `.env` 파일을 사용하거나 시스템 환경 변수로 등록하세요.

### 필수 항목 (Required)

| Key                                | Description                                                                                                         |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| `SLACK_WEBHOOK`                    | 알림을 보낼 Slack Incoming Webhook URL입니다.                                                                       |
| `OPENAI_KEY`                       | OpenAI(기본값) 사용 시 필요한 API Key입니다.                                                                        |
| `OPENROUTER_API_KEY`               | OpenRouter 사용 시 API Key입니다. (`LLM_KEY`로 대체 가능)                                                           |
| `ANTHROPIC_KEY`                    | Anthropic 사용 시 필요한 API Key입니다.                                                                             |
| `GOOGLE_API_KEY` 또는 `GEMINI_KEY` | Google Gemini 사용 시 필요한 API Key입니다.                                                                         |
| `LLM_KEY`                          | 모든 프로바이더에서 공통으로 사용할 수 있는 범용 API Key입니다. (특정 Key가 없을 경우 엔진에서 이 값을 참조합니다.) |

### 선택 항목 (Optional)

| Key            | Default             | Description                                                                                              |
| :------------- | :------------------ | :------------------------------------------------------------------------------------------------------- |
| `LLM_PROVIDER` | `openai`            | 사용할 LLM 프로바이더입니다. (`openai`, `anthropic`, `google` 또는 `gemini`, 그 외 OpenAI 호환 API 지원) |
| `LLM_MODEL`    | 프로바이더별 기본값 | 사용할 특정 모델 명칭입니다. (예: `gpt-4o-mini`, `claude-3-5-sonnet-20240620`, `gemini-1.5-flash`)       |
| `LLM_BASE_URL` | 프로바이더별 기본값 | OpenAI 호환 API를 사용할 경우 API Endpoint 주소를 설정합니다.                                            |
| `HF_TOKEN`     | (N/A)               | Hugging Face API 접근에 필요한 토큰입니다. (필요 시 설정)                                                |

### OpenRouter로 Gemma 4 31B free 사용하기

`google`/`gemini` 프로바이더를 유지하면서 OpenRouter를 사용하려면 아래처럼 설정하세요.

```bash
export LLM_PROVIDER=google
export LLM_BASE_URL=https://openrouter.ai/api/v1
export LLM_MODEL=google/gemma-4-31b-it:free
export OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY
```

또는 `OPENROUTER_API_KEY` 대신 `LLM_KEY`를 사용해도 됩니다.

## 설치 및 실행

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **실행**
   ```bash
   python monitor.py
   ```

## GitHub Actions 설정

저장소의 `Settings > Secrets and variables > Actions` 메뉴에서 위 환경 변수들을 **Repository secrets**로 등록하면 6시간마다 자동으로 실행됩니다.
