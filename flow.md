[GitHub Actions Cron 실행]
        ↓
[HF Trending API 호출]
        ↓
[이전 실행 결과(JSON)와 diff 비교] ← GitHub 저장소에 캐시
        ↓
[신규 모델만 추출]
        ↓
[모델 info + README.md 조회]
        ↓
[LLM으로 요약 생성] (OpenAI / HF Inference API)
        ↓
[Slack / Discord / 이메일 / Telegram 노티]
