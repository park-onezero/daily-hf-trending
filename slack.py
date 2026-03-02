import requests
import os

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

def notify_slack(model_id, summary, info):
    likes = info.get("likes", 0)
    tag = info.get("pipeline_tag", "-")
    msg = f"🆕 *신규 트렌딩 모델 감지*\n*{model_id}*\n태스크: {tag} | 좋아요: {likes}\n\n{summary}\n🔗 https://huggingface.co/{model_id}"
    requests.post(SLACK_WEBHOOK, json={"text": msg})
